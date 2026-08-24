from app.models.indicator_value import IndicatorValue
from app.repositories.indicator_repository import IndicatorValueRepository
from app.repositories.materiality_evidence_repository import MaterialityEvidenceRepository


class EvidenceService:
    """Maps a canonical indicator to material ESG topics without touching materiality scores."""

    TOPIC_MAP = {
        "air": {"air-quality", "ghg-emissions"},
        "energy": {"energy"},
        "water": {"water"},
        "climate": {"ghg-emissions", "risk-management"},
        "risk": {"risk-management", "water", "energy"},
        "territory": {"biodiversity", "risk-management", "ghg-emissions"},
    }

    def __init__(self, db) -> None:
        self.repository = MaterialityEvidenceRepository(db)

    def topics_for_value(self, value: IndicatorValue) -> set[str]:
        return self.TOPIC_MAP.get(value.indicator.category, set())

    def link_value(self, value: IndicatorValue) -> int:
        topic_codes = self.topics_for_value(value)
        assessments = self.repository.completed_assessments_for_topics(value.organization_id, topic_codes)
        linked = 0
        for assessment in assessments:
            self.repository.create_if_missing(assessment.id, value.id, value.indicator.category)
            linked += 1
        return linked

    def link_existing_for_assessment(self, assessment) -> int:
        """Backfill the latest persisted signals when an assessment is completed after a sync."""
        values = IndicatorValueRepository(self.repository.db).list_for_organization(
            assessment.organization_id, limit=500
        )
        latest_by_indicator: dict[tuple[int, int], IndicatorValue] = {}
        for value in values:
            latest_by_indicator.setdefault((value.site_id, value.indicator_id), value)
        linked = 0
        for value in latest_by_indicator.values():
            if assessment.topic.code not in self.topics_for_value(value):
                continue
            self.repository.create_if_missing(assessment.id, value.id, value.indicator.category)
            linked += 1
        return linked

    def list_for_assessment(self, assessment_id: int):
        return self.repository.list_for_assessment(assessment_id)
