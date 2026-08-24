"""Persistence and scoped lookups for the Sprint 9 Gap & Action Engine."""

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.action_plan import ActionPlan
from app.models.action_task import ActionTask
from app.models.audit_entry import AuditEntry
from app.models.esg_gap import ESGGap
from app.models.esg_opportunity import ESGOpportunity
from app.models.esg_risk import ESGRisk
from app.models.esg_target import ESGTarget
from app.models.esg_topic import ESGTopic
from app.models.indicator_value import IndicatorValue
from app.models.materiality_assessment import MaterialityAssessment
from app.models.organization_esg_topic import OrganizationESGTopic


class GapActionRepository:
    """Repository methods always receive organization_id for IDOR-safe resource access."""

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _target_options():
        return (joinedload(ESGTarget.topic), joinedload(ESGTarget.indicator), joinedload(ESGTarget.site))

    @staticmethod
    def _gap_options():
        return (joinedload(ESGGap.topic), joinedload(ESGGap.indicator), joinedload(ESGGap.site))

    @staticmethod
    def _risk_options():
        return (joinedload(ESGRisk.topic), joinedload(ESGRisk.site), joinedload(ESGRisk.indicator_value))

    @staticmethod
    def _opportunity_options():
        return (
            joinedload(ESGOpportunity.topic),
            joinedload(ESGOpportunity.site),
            joinedload(ESGOpportunity.indicator),
            joinedload(ESGOpportunity.indicator_value),
        )

    @staticmethod
    def _action_options():
        return (
            joinedload(ActionPlan.topic),
            joinedload(ActionPlan.site),
            joinedload(ActionPlan.target),
            joinedload(ActionPlan.gap),
            joinedload(ActionPlan.risk),
            selectinload(ActionPlan.tasks),
        )

    def list_targets(self, organization_id: int) -> list[ESGTarget]:
        return (
            self.db.query(ESGTarget)
            .options(*self._target_options())
            .filter(ESGTarget.organization_id == organization_id)
            .order_by(ESGTarget.target_year, ESGTarget.id)
            .all()
        )

    def get_target(self, organization_id: int, target_id: int) -> ESGTarget | None:
        return (
            self.db.query(ESGTarget)
            .options(*self._target_options())
            .filter(ESGTarget.organization_id == organization_id, ESGTarget.id == target_id)
            .first()
        )

    def create_target(self, organization_id: int, data: dict[str, Any]) -> ESGTarget:
        target = ESGTarget(organization_id=organization_id, **data)
        self.db.add(target)
        self.db.flush()
        return self.get_target(organization_id, target.id)  # type: ignore[return-value]

    def list_gaps(self, organization_id: int) -> list[ESGGap]:
        return (
            self.db.query(ESGGap)
            .options(*self._gap_options())
            .filter(ESGGap.organization_id == organization_id)
            .order_by(ESGGap.status, ESGGap.severity.desc(), ESGGap.updated_at.desc(), ESGGap.id.desc())
            .all()
        )

    def get_gap(self, organization_id: int, gap_id: int) -> ESGGap | None:
        return (
            self.db.query(ESGGap)
            .options(*self._gap_options())
            .filter(ESGGap.organization_id == organization_id, ESGGap.id == gap_id)
            .first()
        )

    def list_risks(self, organization_id: int) -> list[ESGRisk]:
        return (
            self.db.query(ESGRisk)
            .options(*self._risk_options())
            .filter(ESGRisk.organization_id == organization_id)
            .order_by(ESGRisk.status, ESGRisk.risk_score.desc(), ESGRisk.id.desc())
            .all()
        )

    def get_risk(self, organization_id: int, risk_id: int) -> ESGRisk | None:
        return (
            self.db.query(ESGRisk)
            .options(*self._risk_options())
            .filter(ESGRisk.organization_id == organization_id, ESGRisk.id == risk_id)
            .first()
        )

    def list_opportunities(self, organization_id: int) -> list[ESGOpportunity]:
        return (
            self.db.query(ESGOpportunity)
            .options(*self._opportunity_options())
            .filter(ESGOpportunity.organization_id == organization_id)
            .order_by(ESGOpportunity.status, ESGOpportunity.opportunity_score.desc(), ESGOpportunity.id.desc())
            .all()
        )

    def list_actions(self, organization_id: int) -> list[ActionPlan]:
        return (
            self.db.query(ActionPlan)
            .options(*self._action_options())
            .filter(ActionPlan.organization_id == organization_id)
            .order_by(ActionPlan.status, ActionPlan.due_date.nullslast(), ActionPlan.id.desc())
            .all()
        )

    def get_action(self, organization_id: int, action_id: int) -> ActionPlan | None:
        return (
            self.db.query(ActionPlan)
            .options(*self._action_options())
            .filter(ActionPlan.organization_id == organization_id, ActionPlan.id == action_id)
            .first()
        )

    def create_action(self, organization_id: int, data: dict[str, Any]) -> ActionPlan:
        action = ActionPlan(organization_id=organization_id, **data)
        self.db.add(action)
        self.db.flush()
        return self.get_action(organization_id, action.id)  # type: ignore[return-value]

    def get_task(self, organization_id: int, action_id: int, task_id: int) -> ActionTask | None:
        return (
            self.db.query(ActionTask)
            .join(ActionTask.action_plan)
            .filter(
                ActionPlan.organization_id == organization_id,
                ActionTask.action_plan_id == action_id,
                ActionTask.id == task_id,
            )
            .first()
        )

    def create_task(self, action: ActionPlan, data: dict[str, Any]) -> ActionTask:
        task = ActionTask(action_plan_id=action.id, **data)
        self.db.add(task)
        self.db.flush()
        self.refresh_action_progress(action)
        return task

    def refresh_action_progress(self, action: ActionPlan) -> ActionPlan:
        self.db.flush()
        tasks = [task for task in action.tasks if task.status != "cancelled"]
        if not tasks:
            action.progress_percentage = 0.0
            if action.status == "completed":
                action.status = "planned"
                action.completed_at = None
            return action
        completed = sum(task.status == "completed" for task in tasks)
        action.progress_percentage = round(completed / len(tasks) * 100, 2)
        if completed == len(tasks):
            action.status = "completed"
            action.completed_at = datetime.now(UTC)
        elif action.status == "completed":
            action.status = "in_progress"
            action.completed_at = None
        return action

    def latest_value(
        self, organization_id: int, indicator_id: int, site_id: int | None
    ) -> IndicatorValue | None:
        query = (
            self.db.query(IndicatorValue)
            .options(joinedload(IndicatorValue.indicator), joinedload(IndicatorValue.site))
            .filter(
                IndicatorValue.organization_id == organization_id,
                IndicatorValue.indicator_id == indicator_id,
            )
        )
        if site_id is not None:
            query = query.filter(IndicatorValue.site_id == site_id)
        return query.order_by(IndicatorValue.collected_at.desc(), IndicatorValue.id.desc()).first()

    def latest_values(self, organization_id: int) -> list[IndicatorValue]:
        values = (
            self.db.query(IndicatorValue)
            .options(joinedload(IndicatorValue.indicator), joinedload(IndicatorValue.site))
            .filter(IndicatorValue.organization_id == organization_id)
            .order_by(IndicatorValue.collected_at.desc(), IndicatorValue.id.desc())
            .all()
        )
        latest: dict[tuple[int, int], IndicatorValue] = {}
        for value in values:
            latest.setdefault((value.site_id, value.indicator_id), value)
        return list(latest.values())

    def completed_assessment(self, organization_id: int, topic_id: int) -> MaterialityAssessment | None:
        return (
            self.db.query(MaterialityAssessment)
            .filter(
                MaterialityAssessment.organization_id == organization_id,
                MaterialityAssessment.topic_id == topic_id,
                MaterialityAssessment.status == "completed",
            )
            .order_by(MaterialityAssessment.reporting_year.desc(), MaterialityAssessment.id.desc())
            .first()
        )

    def enabled_topic_by_code(self, organization_id: int, code: str) -> ESGTopic | None:
        return (
            self.db.query(ESGTopic)
            .join(OrganizationESGTopic, OrganizationESGTopic.topic_id == ESGTopic.id)
            .filter(
                OrganizationESGTopic.organization_id == organization_id,
                OrganizationESGTopic.enabled.is_(True),
                ESGTopic.code == code,
            )
            .first()
        )

    def upsert_gap(self, organization_id: int, fingerprint: str, data: dict[str, Any]) -> tuple[ESGGap, bool]:
        record = (
            self.db.query(ESGGap)
            .filter(ESGGap.organization_id == organization_id, ESGGap.fingerprint == fingerprint)
            .first()
        )
        created = record is None
        if record is None:
            record = ESGGap(organization_id=organization_id, fingerprint=fingerprint, **data)
            self.db.add(record)
        else:
            for key, value in data.items():
                setattr(record, key, value)
            record.status = "open"
            record.resolved_at = None
        self.db.flush()
        return record, created

    def upsert_risk(self, organization_id: int, fingerprint: str, data: dict[str, Any]) -> tuple[ESGRisk, bool]:
        record = (
            self.db.query(ESGRisk)
            .filter(ESGRisk.organization_id == organization_id, ESGRisk.fingerprint == fingerprint)
            .first()
        )
        created = record is None
        if record is None:
            record = ESGRisk(organization_id=organization_id, fingerprint=fingerprint, **data)
            self.db.add(record)
        else:
            for key, value in data.items():
                setattr(record, key, value)
            if record.status == "resolved":
                record.status = "open"
        self.db.flush()
        return record, created

    def upsert_opportunity(
        self, organization_id: int, fingerprint: str, data: dict[str, Any]
    ) -> tuple[ESGOpportunity, bool]:
        record = (
            self.db.query(ESGOpportunity)
            .filter(ESGOpportunity.organization_id == organization_id, ESGOpportunity.fingerprint == fingerprint)
            .first()
        )
        created = record is None
        if record is None:
            record = ESGOpportunity(organization_id=organization_id, fingerprint=fingerprint, **data)
            self.db.add(record)
        else:
            for key, value in data.items():
                setattr(record, key, value)
            if record.status == "dismissed":
                record.status = "open"
        self.db.flush()
        return record, created

    def resolve_absent(self, organization_id: int, model: Any, fingerprints: Iterable[str]) -> int:
        fingerprint_set = set(fingerprints)
        query = self.db.query(model).filter(model.organization_id == organization_id)
        if model is ESGGap:
            records = query.filter(model.status == "open").all()
            for record in records:
                if record.fingerprint not in fingerprint_set:
                    record.status = "resolved"
                    record.resolved_at = datetime.now(UTC)
        elif model is ESGRisk:
            records = query.filter(model.status.in_(("open", "mitigating"))).all()
            for record in records:
                if record.fingerprint not in fingerprint_set:
                    record.status = "resolved"
        else:
            records = query.filter(model.status.in_(("open", "in_progress"))).all()
            for record in records:
                if record.fingerprint not in fingerprint_set:
                    record.status = "dismissed"
        self.db.flush()
        return sum(record.fingerprint not in fingerprint_set for record in records)

    def audit(
        self,
        organization_id: int,
        entity_type: str,
        entity_id: int | None,
        action: str,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        source: str = "api",
    ) -> AuditEntry:
        entry = AuditEntry(
            organization_id=organization_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            source=source,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_audit(self, organization_id: int, limit: int = 100) -> list[AuditEntry]:
        return (
            self.db.query(AuditEntry)
            .filter(AuditEntry.organization_id == organization_id)
            .order_by(AuditEntry.created_at.desc(), AuditEntry.id.desc())
            .limit(limit)
            .all()
        )
