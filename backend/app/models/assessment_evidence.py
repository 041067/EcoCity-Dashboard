from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class AssessmentEvidence(Base):
    __tablename__ = "assessment_evidence"
    __table_args__ = (
        CheckConstraint(
            "evidence_type IN ('manual', 'internal_data', 'external_data', 'document', 'stakeholder')",
            name="ck_assessment_evidence_type",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    materiality_assessment_id = Column(
        Integer, ForeignKey("materiality_assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type = Column(String(20), nullable=False)
    source = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    materiality_assessment = relationship("MaterialityAssessment", back_populates="evidences")
