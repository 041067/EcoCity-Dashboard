from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class MaterialityAssessment(Base):
    """An annual, explainable materiality evaluation for one ESG topic."""

    __tablename__ = "materiality_assessments"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "topic_id",
            "reporting_year",
            name="uq_materiality_assessments_organization_topic_year",
        ),
        CheckConstraint("reporting_year BETWEEN 2000 AND 2100", name="ck_materiality_reporting_year"),
        CheckConstraint(
            "status IN ('draft', 'in_review', 'completed')", name="ck_materiality_assessments_status"
        ),
        CheckConstraint(
            "priority_level IS NULL OR priority_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_materiality_assessments_priority",
        ),
        CheckConstraint(
            "impact_score IS NULL OR impact_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_impact_score",
        ),
        CheckConstraint(
            "financial_score IS NULL OR financial_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_financial_score",
        ),
        CheckConstraint(
            "stakeholder_score IS NULL OR stakeholder_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_stakeholder_score",
        ),
        CheckConstraint(
            "materiality_score IS NULL OR materiality_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_score",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)
    impact_score = Column(Float, nullable=True)
    financial_score = Column(Float, nullable=True)
    stakeholder_score = Column(Float, nullable=True)
    materiality_score = Column(Float, nullable=True, index=True)
    priority_level = Column(String(12), nullable=True, index=True)
    status = Column(String(16), nullable=False, default="draft", server_default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="materiality_assessments")
    topic = relationship("ESGTopic", back_populates="materiality_assessments")
    impact_assessment = relationship(
        "ImpactAssessment", back_populates="materiality_assessment", uselist=False, cascade="all, delete-orphan"
    )
    financial_assessment = relationship(
        "FinancialAssessment", back_populates="materiality_assessment", uselist=False, cascade="all, delete-orphan"
    )
    stakeholder_assessments = relationship(
        "StakeholderAssessment", back_populates="materiality_assessment", cascade="all, delete-orphan"
    )
    evidences = relationship(
        "AssessmentEvidence", back_populates="materiality_assessment", cascade="all, delete-orphan"
    )
    external_evidences = relationship(
        "MaterialityEvidence", back_populates="materiality_assessment", cascade="all, delete-orphan"
    )
    gaps = relationship("ESGGap", back_populates="assessment")
