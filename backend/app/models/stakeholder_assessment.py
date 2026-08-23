from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class StakeholderAssessment(Base):
    __tablename__ = "stakeholder_assessments"
    __table_args__ = (
        UniqueConstraint(
            "materiality_assessment_id",
            "stakeholder_id",
            name="uq_stakeholder_assessments_assessment_stakeholder",
        ),
        CheckConstraint("relevance BETWEEN 1 AND 5", name="ck_stakeholder_assessments_relevance"),
        CheckConstraint("concern_level BETWEEN 1 AND 5", name="ck_stakeholder_assessments_concern"),
        CheckConstraint("influence BETWEEN 1 AND 5", name="ck_stakeholder_assessments_influence"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    materiality_assessment_id = Column(
        Integer, ForeignKey("materiality_assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id", ondelete="RESTRICT"), nullable=False, index=True)
    relevance = Column(Integer, nullable=False)
    concern_level = Column(Integer, nullable=False)
    influence = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    materiality_assessment = relationship("MaterialityAssessment", back_populates="stakeholder_assessments")
    stakeholder = relationship("Stakeholder", back_populates="materiality_assessments")
