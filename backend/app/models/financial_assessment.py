from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.session import Base


class FinancialAssessment(Base):
    __tablename__ = "financial_assessments"
    __table_args__ = (
        CheckConstraint("revenue_impact BETWEEN 1 AND 5", name="ck_financial_assessments_revenue"),
        CheckConstraint("cost_impact BETWEEN 1 AND 5", name="ck_financial_assessments_cost"),
        CheckConstraint("asset_impact BETWEEN 1 AND 5", name="ck_financial_assessments_asset"),
        CheckConstraint("financing_impact BETWEEN 1 AND 5", name="ck_financial_assessments_financing"),
        CheckConstraint("regulatory_impact BETWEEN 1 AND 5", name="ck_financial_assessments_regulatory"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    materiality_assessment_id = Column(
        Integer,
        ForeignKey("materiality_assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    revenue_impact = Column(Integer, nullable=False)
    cost_impact = Column(Integer, nullable=False)
    asset_impact = Column(Integer, nullable=False)
    financing_impact = Column(Integer, nullable=False)
    regulatory_impact = Column(Integer, nullable=False)

    materiality_assessment = relationship("MaterialityAssessment", back_populates="financial_assessment")
