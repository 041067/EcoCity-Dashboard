from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class ESGTarget(Base):
    """An organization-owned target whose progress is calculated server-side."""

    __tablename__ = "esg_targets"
    __table_args__ = (
        CheckConstraint("baseline_year BETWEEN 2000 AND 2100", name="ck_esg_targets_baseline_year"),
        CheckConstraint("target_year BETWEEN 2000 AND 2100", name="ck_esg_targets_target_year"),
        CheckConstraint("target_year > baseline_year", name="ck_esg_targets_year_order"),
        CheckConstraint(
            "status IN ('planned', 'active', 'achieved', 'cancelled')", name="ck_esg_targets_status"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey("esg_indicators.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    baseline_value = Column(Float, nullable=False)
    baseline_year = Column(Integer, nullable=False)
    target_value = Column(Float, nullable=False)
    target_year = Column(Integer, nullable=False)
    unit = Column(String(40), nullable=False)
    status = Column(String(16), nullable=False, default="active", server_default="active", index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="targets")
    site = relationship("Site", back_populates="targets")
    topic = relationship("ESGTopic", back_populates="targets")
    indicator = relationship("ESGIndicator", back_populates="targets")
    gaps = relationship("ESGGap", back_populates="target")
    action_plans = relationship("ActionPlan", back_populates="target")
