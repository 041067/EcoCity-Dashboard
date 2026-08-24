from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
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


class ActionPlan(Base):
    """An execution plan linked to a Gap, Risk, Target, or ESG topic."""

    __tablename__ = "action_plans"
    __table_args__ = (
        CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_action_plans_priority"),
        CheckConstraint("status IN ('planned', 'in_progress', 'blocked', 'completed', 'cancelled')", name="ck_action_plans_status"),
        CheckConstraint("progress_percentage BETWEEN 0 AND 100", name="ck_action_plans_progress"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("esg_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    gap_id = Column(Integer, ForeignKey("esg_gaps.id", ondelete="SET NULL"), nullable=True, index=True)
    risk_id = Column(Integer, ForeignKey("esg_risks.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(240), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(12), nullable=False, default="medium", server_default="medium", index=True)
    status = Column(String(16), nullable=False, default="planned", server_default="planned", index=True)
    responsible_area = Column(String(160), nullable=True)
    due_date = Column(Date, nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    progress_percentage = Column(Float, nullable=False, default=0.0, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="action_plans")
    site = relationship("Site", back_populates="action_plans")
    topic = relationship("ESGTopic", back_populates="action_plans")
    target = relationship("ESGTarget", back_populates="action_plans")
    gap = relationship("ESGGap", back_populates="action_plans")
    risk = relationship("ESGRisk", back_populates="action_plans")
    tasks = relationship("ActionTask", back_populates="action_plan", cascade="all, delete-orphan")
