"""Build a bounded, traceable ESG context without making the LLM query the database."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import settings
from app.models.materiality_assessment import MaterialityAssessment
from app.models.materiality_evidence import MaterialityEvidence
from app.models.organization_esg_topic import OrganizationESGTopic
from app.repositories.gap_action_repository import GapActionRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.ai_copilot import DataSufficiency
from app.services.gap_action_service import GapService


def _safe_text(value: str | None, limit: int = 600) -> str | None:
    if value is None:
        return None
    normalized = " ".join(str(value).replace("\x00", " ").split())
    return normalized[:limit]


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


@dataclass(frozen=True)
class ESGContext:
    data: dict[str, Any]
    context_hash: str
    data_sufficiency: DataSufficiency
    allowed_evidence_ids: frozenset[str]
    allowed_topic_ids: frozenset[int]
    reporting_year: int

    def prompt_json(self) -> str:
        return json.dumps(self.data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


class ESGContextService:
    """Collects only high-value records in deterministic priority order."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.organization_repo = OrganizationRepository(db)
        self.site_repo = SiteRepository(db)
        self.gap_repo = GapActionRepository(db)

    def build(self, organization_id: int, reporting_year: int | None = None) -> ESGContext:
        organization = self.organization_repo.get_by_id(organization_id)
        if organization is None:
            raise LookupError("Organization not found")

        enabled_topics = (
            self.db.query(OrganizationESGTopic)
            .options(joinedload(OrganizationESGTopic.topic))
            .filter(
                OrganizationESGTopic.organization_id == organization_id,
                OrganizationESGTopic.enabled.is_(True),
            )
            .order_by(OrganizationESGTopic.priority.desc(), OrganizationESGTopic.topic_id)
            .all()
        )
        assessments_query = (
            self.db.query(MaterialityAssessment)
            .options(
                joinedload(MaterialityAssessment.topic),
                selectinload(MaterialityAssessment.evidences),
                selectinload(MaterialityAssessment.external_evidences).joinedload(
                    MaterialityEvidence.indicator_value
                ),
            )
            .filter(
                MaterialityAssessment.organization_id == organization_id,
                MaterialityAssessment.status == "completed",
            )
        )
        if reporting_year is not None:
            assessments_query = assessments_query.filter(MaterialityAssessment.reporting_year == reporting_year)
        assessments = assessments_query.order_by(
            MaterialityAssessment.materiality_score.desc().nullslast(),
            MaterialityAssessment.reporting_year.desc(),
            MaterialityAssessment.id.desc(),
        ).all()

        inferred_year = reporting_year or (assessments[0].reporting_year if assessments else datetime.now(UTC).year)
        sites = self.site_repo.list_by_organization(organization_id)
        latest_values = self.gap_repo.latest_values(organization_id)
        risks = [risk for risk in self.gap_repo.list_risks(organization_id) if risk.status != "resolved"]
        gaps = [gap for gap in self.gap_repo.list_gaps(organization_id) if gap.status == "open"]
        opportunities = [
            opportunity
            for opportunity in self.gap_repo.list_opportunities(organization_id)
            if opportunity.status in {"open", "in_progress"}
        ]
        targets = self.gap_repo.list_targets(organization_id)
        actions = [
            action
            for action in self.gap_repo.list_actions(organization_id)
            if action.status not in {"completed", "cancelled"}
        ]

        assessment_items = [self._assessment_item(item) for item in assessments[:8]]
        evidence_items = [self._indicator_evidence(value) for value in self._prioritize_values(latest_values)[:16]]
        manual_evidence = self._manual_evidence(assessments[:8])[:10]
        evidence_items.extend(manual_evidence)

        data = {
            "organization": {
                "id": organization.id,
                "name": _safe_text(organization.name, 200),
                "type": organization.organization_type,
                "industry_sector": _safe_text(organization.industry_sector, 120),
                "country": _safe_text(organization.country, 100),
                "description": _safe_text(organization.description, 600),
            },
            "sites": [
                {
                    "id": site.id,
                    "name": _safe_text(site.name, 160),
                    "type": site.site_type,
                    "city": _safe_text(site.city.name if site.city else None, 100),
                }
                for site in sites[:12]
            ],
            "material_topics": assessment_items,
            "evidence": evidence_items,
            "gaps": [self._gap_item(gap) for gap in gaps[:10]],
            "risks": [self._risk_item(risk) for risk in risks[:10]],
            "opportunities": [self._opportunity_item(item) for item in opportunities[:8]],
            "targets": [self._target_item(target) for target in targets[:10]],
            "actions": [self._action_item(action) for action in actions[:8]],
            "context_rules": {
                "official_scores_are_deterministic": True,
                "evidence_id_prefixes": ["IND-", "EVD-"],
            },
        }
        data = self._fit_budget(data)
        evidence_ids = frozenset(item["id"] for item in data["evidence"])
        topic_ids = {
            link.topic_id for link in enabled_topics
        } | {item["topic_id"] for item in data["material_topics"]}
        sufficiency = self._data_sufficiency(
            enabled_topic_count=len(enabled_topics),
            assessments=assessments,
            values=latest_values,
            sites_count=len(sites),
        )
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return ESGContext(
            data=data,
            context_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            data_sufficiency=sufficiency,
            allowed_evidence_ids=evidence_ids,
            allowed_topic_ids=frozenset(topic_ids),
            reporting_year=inferred_year,
        )

    @staticmethod
    def _assessment_item(assessment: MaterialityAssessment) -> dict[str, Any]:
        return {
            "id": assessment.id,
            "topic_id": assessment.topic_id,
            "topic": _safe_text(assessment.topic.name, 160),
            "reporting_year": assessment.reporting_year,
            "materiality_score": assessment.materiality_score,
            "priority": assessment.priority_level,
        }

    @staticmethod
    def _indicator_evidence(value) -> dict[str, Any]:
        return {
            "id": f"IND-{value.id:04d}",
            "type": "indicator_value",
            "topic_hint": _safe_text(value.indicator.category, 80),
            "indicator": _safe_text(value.indicator.name, 180),
            "value": value.value,
            "unit": _safe_text(value.unit, 40),
            "source": _safe_text(value.source, 80),
            "observed_at": _iso(value.observed_at),
            "collected_at": _iso(value.collected_at),
            "quality_score": value.quality_score,
            "freshness_score": value.freshness_score,
            "confidence_score": value.confidence_score,
        }

    @staticmethod
    def _manual_evidence(assessments: list[MaterialityAssessment]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for assessment in assessments:
            for evidence in assessment.evidences:
                items.append(
                    {
                        "id": f"EVD-{evidence.id:04d}",
                        "type": evidence.evidence_type,
                        "topic_id": assessment.topic_id,
                        "topic": _safe_text(assessment.topic.name, 160),
                        "source": _safe_text(evidence.source, 180),
                        "description": _safe_text(evidence.description, 500),
                        "reference": _safe_text(evidence.reference, 300),
                    }
                )
        return items

    @staticmethod
    def _gap_item(gap) -> dict[str, Any]:
        return {
            "id": gap.id,
            "topic_id": gap.topic_id,
            "topic": _safe_text(gap.topic.name, 160),
            "severity": gap.severity,
            "current_value": gap.current_value,
            "target_value": gap.target_value,
            "unit": _safe_text(gap.unit, 40),
            "description": _safe_text(gap.description, 600),
            "source": _safe_text(gap.source, 100),
        }

    @staticmethod
    def _risk_item(risk) -> dict[str, Any]:
        return {
            "id": risk.id,
            "topic_id": risk.topic_id,
            "topic": _safe_text(risk.topic.name, 160),
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "description": _safe_text(risk.description, 600),
            "source": _safe_text(risk.source, 100),
            "evidence_id": f"IND-{risk.indicator_value_id:04d}" if risk.indicator_value_id else None,
        }

    @staticmethod
    def _opportunity_item(opportunity) -> dict[str, Any]:
        return {
            "id": opportunity.id,
            "topic_id": opportunity.topic_id,
            "topic": _safe_text(opportunity.topic.name, 160),
            "opportunity_type": _safe_text(opportunity.opportunity_type, 100),
            "opportunity_score": opportunity.opportunity_score,
            "priority": opportunity.priority,
            "description": _safe_text(opportunity.description, 600),
            "evidence_id": (
                f"IND-{opportunity.indicator_value_id:04d}" if opportunity.indicator_value_id else None
            ),
        }

    def _target_item(self, target) -> dict[str, Any]:
        latest = self.gap_repo.latest_value(target.organization_id, target.indicator_id, target.site_id)
        current = latest.value if latest else None
        progress, tracking = GapService.tracking(
            target.baseline_value,
            target.baseline_year,
            target.target_value,
            target.target_year,
            current,
            target.indicator.direction,
        )
        return {
            "id": target.id,
            "topic_id": target.topic_id,
            "topic": _safe_text(target.topic.name, 160),
            "name": _safe_text(target.name, 200),
            "current_value": current,
            "target_value": target.target_value,
            "unit": _safe_text(target.unit, 40),
            "target_year": target.target_year,
            "progress_percentage": progress,
            "tracking_status": tracking,
            "evidence_id": f"IND-{latest.id:04d}" if latest else None,
        }

    @staticmethod
    def _action_item(action) -> dict[str, Any]:
        return {
            "id": action.id,
            "topic_id": action.topic_id,
            "topic": _safe_text(action.topic.name, 160),
            "title": _safe_text(action.title, 240),
            "priority": action.priority,
            "status": action.status,
            "progress_percentage": action.progress_percentage,
            "due_date": action.due_date.isoformat() if action.due_date else None,
        }

    @staticmethod
    def _prioritize_values(values: list) -> list:
        return sorted(
            values,
            key=lambda value: (
                float(value.confidence_score or 0),
                float(value.quality_score or 0),
                float(value.freshness_score or 0),
                value.id,
            ),
            reverse=True,
        )

    @staticmethod
    def _fit_budget(data: dict[str, Any]) -> dict[str, Any]:
        """Preserve priority ordering while reducing only lower-value tail entries."""
        priority_keys = ("actions", "evidence", "opportunities", "gaps", "risks", "targets", "material_topics")
        while len(json.dumps(data, ensure_ascii=False, separators=(",", ":"))) > settings.AI_CONTEXT_MAX_CHARS:
            reduced = False
            for key in priority_keys:
                if len(data[key]) > 1:
                    data[key].pop()
                    reduced = True
                    break
            if not reduced:
                break
        return data

    @staticmethod
    def _data_sufficiency(
        *, enabled_topic_count: int, assessments: list, values: list, sites_count: int
    ) -> DataSufficiency:
        evidence_count = len(values)
        covered_topics = len({assessment.topic_id for assessment in assessments})
        coverage = round(covered_topics / enabled_topic_count * 100, 2) if enabled_topic_count else 0.0
        quality = (
            mean(
                (float(value.quality_score) + float(value.freshness_score) + float(value.confidence_score)) / 3
                for value in values
            )
            if values
            else 0.0
        )
        availability = min(100.0, evidence_count / max(1, sites_count) * 50)
        score = round(availability * 0.45 + coverage * 0.30 + quality * 0.25, 2)
        missing: list[str] = []
        if not assessments:
            missing.append("Avaliações de materialidade concluídas")
        if not values:
            missing.append("Valores de indicadores com evidência")
        if enabled_topic_count and coverage < 100:
            missing.append("Cobertura de materialidade para todos os temas ESG ativos")
        if sites_count == 0:
            missing.append("Unidades organizacionais cadastradas")
        level = "high" if score >= 70 else "medium" if score >= 40 else "low"
        return DataSufficiency(
            level=level,
            score=score,
            evidence_count=evidence_count,
            coverage_percentage=coverage,
            average_quality=round(quality, 2),
            missing=missing,
        )
