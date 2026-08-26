from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            "organization_type IN ('company', 'municipality', 'public_agency', 'university', 'other')",
            name="ck_organizations_type",
        ),
        CheckConstraint("employee_count IS NULL OR employee_count >= 0", name="ck_organizations_employee_count"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    organization_type = Column(String(30), nullable=False)
    industry_sector = Column(String(120), nullable=True)
    document = Column(String(40), nullable=True, unique=True)
    country = Column(String(100), nullable=False, default="Brasil")
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sites = relationship("Site", back_populates="organization", cascade="all, delete-orphan")
    stakeholders = relationship("Stakeholder", back_populates="organization", cascade="all, delete-orphan")
    esg_profile = relationship(
        "ESGProfile", back_populates="organization", uselist=False, cascade="all, delete-orphan"
    )
    esg_topic_links = relationship(
        "OrganizationESGTopic", back_populates="organization", cascade="all, delete-orphan"
    )
    materiality_assessments = relationship(
        "MaterialityAssessment", back_populates="organization", cascade="all, delete-orphan"
    )
    indicator_values = relationship("IndicatorValue", back_populates="organization", cascade="all, delete-orphan")
    targets = relationship("ESGTarget", back_populates="organization", cascade="all, delete-orphan")
    gaps = relationship("ESGGap", back_populates="organization", cascade="all, delete-orphan")
    risks = relationship("ESGRisk", back_populates="organization", cascade="all, delete-orphan")
    opportunities = relationship("ESGOpportunity", back_populates="organization", cascade="all, delete-orphan")
    action_plans = relationship("ActionPlan", back_populates="organization", cascade="all, delete-orphan")
    esg_reports = relationship("ESGReport", cascade="all, delete-orphan")
    ai_recommendations = relationship("AIRecommendation", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsage", cascade="all, delete-orphan")
    audit_entries = relationship("AuditEntry", back_populates="organization", cascade="all, delete-orphan")
