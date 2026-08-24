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


class ESGRisk(Base):
    """An explainable 1--5 likelihood/impact risk derived from evidence."""

    __tablename__ = "esg_risks"
    __table_args__ = (
        UniqueConstraint("organization_id", "fingerprint", name="uq_esg_risks_organization_fingerprint"),
        CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_esg_risks_likelihood"),
        CheckConstraint("impact BETWEEN 1 AND 5", name="ck_esg_risks_impact"),
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_esg_risks_score"),
        CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name="ck_esg_risks_level"),
        CheckConstraint("status IN ('open', 'mitigating', 'resolved')", name="ck_esg_risks_status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    indicator_value_id = Column(Integer, ForeignKey("indicator_values.id", ondelete="SET NULL"), nullable=True, index=True)
    fingerprint = Column(String(128), nullable=False)
    risk_type = Column(String(80), nullable=False)
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False, index=True)
    risk_level = Column(String(12), nullable=False, index=True)
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    status = Column(String(16), nullable=False, default="open", server_default="open", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="risks")
    site = relationship("Site", back_populates="risks")
    topic = relationship("ESGTopic", back_populates="risks")
    indicator_value = relationship("IndicatorValue", back_populates="risks")
    action_plans = relationship("ActionPlan", back_populates="risk")
