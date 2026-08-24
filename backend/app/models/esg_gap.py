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


class ESGGap(Base):
    """A deterministic variance between the latest measurement and a target."""

    __tablename__ = "esg_gaps"
    __table_args__ = (
        UniqueConstraint("organization_id", "fingerprint", name="uq_esg_gaps_organization_fingerprint"),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name="ck_esg_gaps_severity"),
        CheckConstraint("status IN ('open', 'resolved')", name="ck_esg_gaps_status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey("esg_indicators.id", ondelete="RESTRICT"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("esg_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    assessment_id = Column(Integer, ForeignKey("materiality_assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    fingerprint = Column(String(128), nullable=False)
    gap_type = Column(String(80), nullable=False, default="target_variance")
    severity = Column(String(12), nullable=False, index=True)
    status = Column(String(12), nullable=False, default="open", server_default="open", index=True)
    current_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    gap_value = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="gaps")
    site = relationship("Site", back_populates="gaps")
    topic = relationship("ESGTopic", back_populates="gaps")
    indicator = relationship("ESGIndicator", back_populates="gaps")
    target = relationship("ESGTarget", back_populates="gaps")
    assessment = relationship("MaterialityAssessment", back_populates="gaps")
    action_plans = relationship("ActionPlan", back_populates="gap")
