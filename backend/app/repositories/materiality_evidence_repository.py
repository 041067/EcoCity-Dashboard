from sqlalchemy.orm import Session, joinedload

from app.models.esg_topic import ESGTopic
from app.models.indicator_value import IndicatorValue
from app.models.materiality_assessment import MaterialityAssessment
from app.models.materiality_evidence import MaterialityEvidence


class MaterialityEvidenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_if_missing(self, assessment_id: int, value_id: int, relevance: str) -> MaterialityEvidence:
        evidence = (
            self.db.query(MaterialityEvidence)
            .filter(
                MaterialityEvidence.materiality_assessment_id == assessment_id,
                MaterialityEvidence.indicator_value_id == value_id,
            )
            .first()
        )
        if evidence is None:
            evidence = MaterialityEvidence(
                materiality_assessment_id=assessment_id,
                indicator_value_id=value_id,
                relevance=relevance,
            )
            self.db.add(evidence)
            self.db.flush()
        return evidence

    def list_for_assessment(self, assessment_id: int) -> list[MaterialityEvidence]:
        return (
            self.db.query(MaterialityEvidence)
            .options(
                joinedload(MaterialityEvidence.indicator_value).joinedload(IndicatorValue.indicator),
                joinedload(MaterialityEvidence.indicator_value).joinedload(IndicatorValue.site),
            )
            .filter(MaterialityEvidence.materiality_assessment_id == assessment_id)
            .order_by(MaterialityEvidence.created_at.desc())
            .all()
        )

    def completed_assessments_for_topics(
        self, organization_id: int, topic_codes: set[str]
    ) -> list[MaterialityAssessment]:
        if not topic_codes:
            return []
        return (
            self.db.query(MaterialityAssessment)
            .join(MaterialityAssessment.topic)
            .filter(
                MaterialityAssessment.organization_id == organization_id,
                MaterialityAssessment.status == "completed",
                ESGTopic.code.in_(topic_codes),
            )
            .all()
        )
