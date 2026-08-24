from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class ActionTask(Base):
    __tablename__ = "action_tasks"
    __table_args__ = (
        CheckConstraint("status IN ('planned', 'in_progress', 'blocked', 'completed', 'cancelled')", name="ck_action_tasks_status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_plan_id = Column(Integer, ForeignKey("action_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(240), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(16), nullable=False, default="planned", server_default="planned", index=True)
    due_date = Column(Date, nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    action_plan = relationship("ActionPlan", back_populates="tasks")
