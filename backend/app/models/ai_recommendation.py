from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class AIRecommendation(Base):
    """A proposed action. It only becomes an ActionPlan after explicit approval."""

    __tablename__ = "ai_recommendations"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')", name="ck_ai_recommendations_priority"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'dismissed', 'converted')",
            name="ck_ai_recommendations_status",
        ),
        CheckConstraint(
            "time_horizon IN ('immediate', 'short_term', 'medium_term', 'long_term')",
            name="ck_ai_recommendations_horizon",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(240), nullable=False)
    rationale = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=False)
    time_horizon = Column(String(20), nullable=False)
    priority = Column(String(12), nullable=False, index=True)
    evidence_ids = Column(JSON, nullable=False)
    context_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(16), nullable=False, default="pending", server_default="pending", index=True)
    action_plan_id = Column(Integer, ForeignKey("action_plans.id", ondelete="SET NULL"), nullable=True)
    model = Column(String(120), nullable=False)
    prompt_version = Column(String(80), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    topic = relationship("ESGTopic")
