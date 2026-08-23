from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.session import Base


class ImpactAssessment(Base):
    __tablename__ = "impact_assessments"
    __table_args__ = (
        CheckConstraint("severity BETWEEN 1 AND 5", name="ck_impact_assessments_severity"),
        CheckConstraint("scope BETWEEN 1 AND 5", name="ck_impact_assessments_scope"),
        CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_impact_assessments_likelihood"),
        CheckConstraint("remediability BETWEEN 1 AND 5", name="ck_impact_assessments_remediability"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    materiality_assessment_id = Column(
        Integer,
        ForeignKey("materiality_assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    severity = Column(Integer, nullable=False)
    scope = Column(Integer, nullable=False)
    likelihood = Column(Integer, nullable=False)
    remediability = Column(Integer, nullable=False)

    materiality_assessment = relationship("MaterialityAssessment", back_populates="impact_assessment")
