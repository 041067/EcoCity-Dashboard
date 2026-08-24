"""Deterministic and explainable calculations for the Sprint 9 Gap & Action Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.models.esg_gap import ESGGap
from app.models.esg_opportunity import ESGOpportunity
from app.models.esg_risk import ESGRisk
from app.repositories.gap_action_repository import GapActionRepository
from app.services.esg_data.evidence_service import EvidenceService

PRIORITY_WEIGHTS = {
    "materiality": 0.35,
    "gap_severity": 0.30,
    "risk": 0.25,
    "evidence_confidence": 0.10,
}


def priority_level(score: float) -> str:
    if score < 40:
        return "low"
    if score < 60:
        return "medium"
    if score < 80:
        return "high"
    return "critical"


class GapService:
    """Direction-aware target variance and target-tracking calculations."""

    @staticmethod
    def gap_value(current: float, target: float, direction: str) -> float:
        if direction == "lower_is_better":
            return round(max(0.0, current - target), 4)
        return round(max(0.0, target - current), 4)

    @classmethod
    def severity(cls, current: float, target: float, direction: str) -> str | None:
        gap = cls.gap_value(current, target, direction)
        if gap == 0:
            return None
        ratio = gap / max(abs(target), 1.0) * 100
        if ratio < 10:
            return "low"
        if ratio < 25:
            return "medium"
        if ratio < 50:
            return "high"
        return "critical"

    @classmethod
    def tracking(
        cls,
        baseline_value: float,
        baseline_year: int,
        target_value: float,
        target_year: int,
        current_value: float | None,
        direction: str,
        current_year: int | None = None,
    ) -> tuple[float | None, str]:
        if current_value is None:
            return None, "no_data"
        if cls.gap_value(current_value, target_value, direction) == 0:
            return 100.0, "achieved"
        denominator = target_value - baseline_value
        if denominator == 0:
            return 0.0, "off_track"
        progress = max(0.0, min(100.0, (current_value - baseline_value) / denominator * 100))
        year = current_year or datetime.now(UTC).year
        expected = max(0.0, min(100.0, (year - baseline_year) / (target_year - baseline_year) * 100))
        if progress >= expected - 10:
            return round(progress, 2), "on_track"
        if progress >= expected - 25:
            return round(progress, 2), "at_risk"
        return round(progress, 2), "off_track"


class RiskService:
    @staticmethod
    def calculate(likelihood: int, impact: int) -> tuple[float, str]:
        score = round(likelihood * impact / 25 * 100, 2)
        return score, priority_level(score)


class OpportunityService:
    @staticmethod
    def calculate(potential_impact: int, feasibility: int) -> tuple[float, str]:
        score = round(potential_impact * feasibility / 25 * 100, 2)
        return score, priority_level(score)


class PriorityService:
    """Ranks topics using the documented 35/30/25/10 weighted methodology."""

    GAP_SCORES = {"low": 25.0, "medium": 50.0, "high": 75.0, "critical": 100.0}

    @classmethod
    def build(
        cls,
        repository: GapActionRepository,
        organization_id: int,
    ) -> list[dict]:
        gaps = [gap for gap in repository.list_gaps(organization_id) if gap.status == "open"]
        risks = [risk for risk in repository.list_risks(organization_id) if risk.status != "resolved"]
        values = repository.latest_values(organization_id)
        topic_ids = {item.topic_id for item in gaps} | {item.topic_id for item in risks}
        results: list[dict] = []
        for topic_id in topic_ids:
            topic = next(
                (item.topic for item in gaps if item.topic_id == topic_id),
                next((item.topic for item in risks if item.topic_id == topic_id), None),
            )
            if topic is None:
                continue
            assessment = repository.completed_assessment(organization_id, topic_id)
            related_values = [
                value
                for value in values
                if topic.code in EvidenceService.TOPIC_MAP.get(value.indicator.category, set())
            ]
            topic_gaps = [gap for gap in gaps if gap.topic_id == topic_id]
            topic_risks = [risk for risk in risks if risk.topic_id == topic_id]
            components = {
                "materiality": float(assessment.materiality_score) if assessment else 0.0,
                "gap_severity": max((cls.GAP_SCORES[gap.severity] for gap in topic_gaps), default=0.0),
                "risk": max((float(risk.risk_score) for risk in topic_risks), default=0.0),
                "evidence_confidence": round(
                    sum(float(value.confidence_score) for value in related_values) / len(related_values), 2
                )
                if related_values
                else 0.0,
            }
            score = round(
                sum(components[name] * weight for name, weight in PRIORITY_WEIGHTS.items()), 2
            )
            evidence_ids = [value.id for value in related_values]
            results.append(
                {
                    "topic_id": topic.id,
                    "topic": topic,
                    "site_id": None,
                    "score": score,
                    "priority": priority_level(score),
                    "breakdown": components,
                    "evidence_ids": evidence_ids,
                    "explanation": (
                        "score = materiality×35% + gap severity×30% + risk×25% + "
                        "evidence confidence×10%"
                    ),
                }
            )
        return sorted(results, key=lambda item: (-item["score"], item["topic"].name))


@dataclass(frozen=True)
class AnalysisResult:
    run_id: str
    created: dict[str, int]
    updated: dict[str, int]
    gaps_open: int
    risks_open: int
    opportunities_open: int


class AnalysisService:
    """Runs idempotent, deterministic gap/risk/opportunity detection from persisted evidence."""

    def __init__(self, repository: GapActionRepository) -> None:
        self.repository = repository

    def run(self, organization_id: int) -> AnalysisResult:
        created = {"gaps": 0, "risks": 0, "opportunities": 0}
        updated = {"gaps": 0, "risks": 0, "opportunities": 0}
        gap_fingerprints = self._detect_gaps(organization_id, created, updated)
        risk_fingerprints = self._detect_risks(organization_id, created, updated)
        opportunity_fingerprints = self._detect_opportunities(organization_id, created, updated)
        self.repository.resolve_absent(organization_id, ESGGap, gap_fingerprints)
        self.repository.resolve_absent(organization_id, ESGRisk, risk_fingerprints)
        self.repository.resolve_absent(organization_id, ESGOpportunity, opportunity_fingerprints)
        gaps_open = sum(gap.status == "open" for gap in self.repository.list_gaps(organization_id))
        risks_open = sum(risk.status != "resolved" for risk in self.repository.list_risks(organization_id))
        opportunities_open = sum(
            opportunity.status in {"open", "in_progress"}
            for opportunity in self.repository.list_opportunities(organization_id)
        )
        run_id = str(uuid4())
        self.repository.audit(
            organization_id,
            "analysis_run",
            None,
            "completed",
            new_value={
                "run_id": run_id,
                "created": created,
                "updated": updated,
                "gaps_open": gaps_open,
                "risks_open": risks_open,
                "opportunities_open": opportunities_open,
            },
            source="analysis_engine",
        )
        return AnalysisResult(run_id, created, updated, gaps_open, risks_open, opportunities_open)

    def _detect_gaps(self, organization_id: int, created: dict[str, int], updated: dict[str, int]) -> list[str]:
        fingerprints: list[str] = []
        for target in self.repository.list_targets(organization_id):
            if target.status in {"cancelled", "achieved"}:
                continue
            value = self.repository.latest_value(organization_id, target.indicator_id, target.site_id)
            if value is None:
                continue
            direction = target.indicator.direction
            severity = GapService.severity(float(value.value), float(target.target_value), direction)
            fingerprint = f"target:{target.id}"
            if severity is None:
                continue
            assessment = self.repository.completed_assessment(organization_id, target.topic_id)
            gap_value = GapService.gap_value(float(value.value), float(target.target_value), direction)
            record, was_created = self.repository.upsert_gap(
                organization_id,
                fingerprint,
                {
                    "site_id": target.site_id,
                    "topic_id": target.topic_id,
                    "indicator_id": target.indicator_id,
                    "target_id": target.id,
                    "assessment_id": assessment.id if assessment else None,
                    "gap_type": "target_variance",
                    "severity": severity,
                    "current_value": float(value.value),
                    "target_value": float(target.target_value),
                    "gap_value": gap_value,
                    "unit": target.unit,
                    "description": f"{target.name}: current value differs from target by {gap_value:g} {target.unit}.",
                    "source": value.source,
                },
            )
            fingerprints.append(record.fingerprint)
            created["gaps"] += int(was_created)
            updated["gaps"] += int(not was_created)
        return fingerprints

    def _detect_risks(self, organization_id: int, created: dict[str, int], updated: dict[str, int]) -> list[str]:
        fingerprints: list[str] = []
        for value in self.repository.latest_values(organization_id):
            if value.indicator.category != "risk":
                continue
            topic_code = "water" if value.indicator.code in {"WATER_DROUGHT_RISK", "WATER_STRESS_SIGNAL"} else "risk-management"
            topic = self.repository.enabled_topic_by_code(organization_id, topic_code)
            if topic is None:
                topic = self.repository.enabled_topic_by_code(organization_id, "risk-management")
            if topic is None:
                continue
            likelihood = max(1, min(5, int(round(float(value.value)))))
            assessment = self.repository.completed_assessment(organization_id, topic.id)
            impact = max(1, min(5, int(round(float(assessment.materiality_score) / 20)))) if assessment else 3
            score, level = RiskService.calculate(likelihood, impact)
            fingerprint = f"risk:{value.site_id}:{value.indicator_id}"
            record, was_created = self.repository.upsert_risk(
                organization_id,
                fingerprint,
                {
                    "site_id": value.site_id,
                    "topic_id": topic.id,
                    "indicator_value_id": value.id,
                    "risk_type": value.indicator.code.lower(),
                    "likelihood": likelihood,
                    "impact": impact,
                    "risk_score": score,
                    "risk_level": level,
                    "description": (
                        f"Derived from {value.indicator.name}={value.value:g}; "
                        f"likelihood {likelihood}/5 and impact {impact}/5."
                    ),
                    "source": value.source,
                },
            )
            fingerprints.append(record.fingerprint)
            created["risks"] += int(was_created)
            updated["risks"] += int(not was_created)
        return fingerprints

    def _detect_opportunities(
        self, organization_id: int, created: dict[str, int], updated: dict[str, int]
    ) -> list[str]:
        topic = self.repository.enabled_topic_by_code(organization_id, "energy")
        if topic is None:
            return []
        fingerprints: list[str] = []
        for value in self.repository.latest_values(organization_id):
            if value.indicator.code != "ENERGY_SOLAR_POTENTIAL" or float(value.value) < 3.5:
                continue
            potential_impact = max(1, min(5, int(round(float(value.value) / 7 * 5))))
            feasibility = 4
            score, priority = OpportunityService.calculate(potential_impact, feasibility)
            fingerprint = f"solar:{value.site_id}:{value.indicator_id}"
            record, was_created = self.repository.upsert_opportunity(
                organization_id,
                fingerprint,
                {
                    "site_id": value.site_id,
                    "topic_id": topic.id,
                    "indicator_id": value.indicator_id,
                    "indicator_value_id": value.id,
                    "opportunity_type": "solar_generation",
                    "potential_impact": potential_impact,
                    "feasibility": feasibility,
                    "opportunity_score": score,
                    "priority": priority,
                    "description": (
                        f"Historical solar potential of {value.value:g} {value.unit} supports a solar feasibility review."
                    ),
                    "evidence_reference": value.source_reference,
                },
            )
            fingerprints.append(record.fingerprint)
            created["opportunities"] += int(was_created)
            updated["opportunities"] += int(not was_created)
        return fingerprints
