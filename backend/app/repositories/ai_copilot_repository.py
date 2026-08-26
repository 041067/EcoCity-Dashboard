"""Scoped persistence for the optional ESG AI Copilot."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session, joinedload

from app.models.ai_recommendation import AIRecommendation
from app.models.ai_usage import AIUsage
from app.models.esg_report import ESGReport


class AICopilotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_cached_report(
        self, organization_id: int, report_type: str, context_hash: str
    ) -> ESGReport | None:
        return (
            self.db.query(ESGReport)
            .filter(
                ESGReport.organization_id == organization_id,
                ESGReport.report_type == report_type,
                ESGReport.context_hash == context_hash,
                ESGReport.status == "completed",
            )
            .order_by(ESGReport.generated_at.desc(), ESGReport.id.desc())
            .first()
        )

    def get_report(self, organization_id: int, report_id: int) -> ESGReport | None:
        return (
            self.db.query(ESGReport)
            .filter(ESGReport.organization_id == organization_id, ESGReport.id == report_id)
            .first()
        )

    def list_reports(self, organization_id: int, limit: int = 50) -> list[ESGReport]:
        return (
            self.db.query(ESGReport)
            .filter(ESGReport.organization_id == organization_id)
            .order_by(ESGReport.generated_at.desc(), ESGReport.id.desc())
            .limit(limit)
            .all()
        )

    def create_report(self, **data) -> ESGReport:
        report = ESGReport(**data)
        self.db.add(report)
        self.db.flush()
        return report

    def find_recommendations(
        self, organization_id: int, context_hash: str
    ) -> list[AIRecommendation]:
        return (
            self.db.query(AIRecommendation)
            .options(joinedload(AIRecommendation.topic))
            .filter(
                AIRecommendation.organization_id == organization_id,
                AIRecommendation.context_hash == context_hash,
            )
            .order_by(AIRecommendation.priority.desc(), AIRecommendation.id.desc())
            .all()
        )

    def list_recommendations(self, organization_id: int, include_dismissed: bool = True) -> list[AIRecommendation]:
        query = (
            self.db.query(AIRecommendation)
            .options(joinedload(AIRecommendation.topic))
            .filter(AIRecommendation.organization_id == organization_id)
        )
        if not include_dismissed:
            query = query.filter(AIRecommendation.status != "dismissed")
        return query.order_by(AIRecommendation.generated_at.desc(), AIRecommendation.id.desc()).all()

    def get_recommendation(self, organization_id: int, recommendation_id: int) -> AIRecommendation | None:
        return (
            self.db.query(AIRecommendation)
            .options(joinedload(AIRecommendation.topic))
            .filter(
                AIRecommendation.organization_id == organization_id,
                AIRecommendation.id == recommendation_id,
            )
            .first()
        )

    def create_recommendation(self, **data) -> AIRecommendation:
        recommendation = AIRecommendation(**data)
        self.db.add(recommendation)
        self.db.flush()
        return recommendation

    def record_usage(
        self,
        organization_id: int,
        operation: str,
        model: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: int = 0,
        status: str = "success",
        error_code: str | None = None,
    ) -> AIUsage:
        usage = AIUsage(
            organization_id=organization_id,
            operation=operation,
            model=model,
            input_tokens=max(0, input_tokens),
            output_tokens=max(0, output_tokens),
            latency_ms=max(0, latency_ms),
            status=status,
            error_code=error_code[:80] if error_code else None,
        )
        self.db.add(usage)
        self.db.flush()
        return usage

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)
