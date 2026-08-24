from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class MaterialityEvidence(Base):
    """Audit link between a value from the evidence layer and a materiality topic assessment."""

    __tablename__ = "materiality_evidence"
    __table_args__ = (
        UniqueConstraint(
            "materiality_assessment_id",
            "indicator_value_id",
            name="uq_materiality_evidence_assessment_value",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    materiality_assessment_id = Column(
        Integer, ForeignKey("materiality_assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    indicator_value_id = Column(
        Integer, ForeignKey("indicator_values.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relevance = Column(String(80), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    materiality_assessment = relationship("MaterialityAssessment", back_populates="external_evidences")
    indicator_value = relationship("IndicatorValue", back_populates="materiality_evidences")
