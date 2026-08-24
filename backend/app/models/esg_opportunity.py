from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class ESGOpportunity(Base):
    """A positive, evidence-backed ESG opportunity ranked by deterministic score."""

    __tablename__ = "esg_opportunities"
    __table_args__ = (
        UniqueConstraint("organization_id", "fingerprint", name="uq_esg_opportunities_organization_fingerprint"),
        CheckConstraint("potential_impact BETWEEN 1 AND 5", name="ck_esg_opportunities_impact"),
        CheckConstraint("feasibility BETWEEN 1 AND 5", name="ck_esg_opportunities_feasibility"),
        CheckConstraint("opportunity_score BETWEEN 0 AND 100", name="ck_esg_opportunities_score"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_esg_opportunities_priority"),
        CheckConstraint("status IN ('open', 'in_progress', 'realized', 'dismissed')", name="ck_esg_opportunities_status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey("esg_indicators.id", ondelete="SET NULL"), nullable=True, index=True)
    indicator_value_id = Column(Integer, ForeignKey("indicator_values.id", ondelete="SET NULL"), nullable=True, index=True)
    fingerprint = Column(String(128), nullable=False)
    opportunity_type = Column(String(80), nullable=False)
    potential_impact = Column(Integer, nullable=False)
    feasibility = Column(Integer, nullable=False)
    opportunity_score = Column(Float, nullable=False, index=True)
    priority = Column(String(12), nullable=False, index=True)
    description = Column(Text, nullable=False)
    evidence_reference = Column(String(1000), nullable=True)
    status = Column(String(16), nullable=False, default="open", server_default="open", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="opportunities")
    site = relationship("Site", back_populates="opportunities")
    topic = relationship("ESGTopic", back_populates="opportunities")
    indicator = relationship("ESGIndicator", back_populates="opportunities")
    indicator_value = relationship("IndicatorValue", back_populates="opportunities")
