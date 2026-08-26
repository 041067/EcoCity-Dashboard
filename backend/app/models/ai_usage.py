from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func

from app.database.session import Base


class AIUsage(Base):
    """Operational telemetry without prompts, answers, keys, or business payloads."""

    __tablename__ = "ai_usage"
    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'failure', 'cache_hit', 'rate_limited')", name="ck_ai_usage_status"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    operation = Column(String(80), nullable=False, index=True)
    model = Column(String(120), nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0, server_default="0")
    output_tokens = Column(Integer, nullable=False, default=0, server_default="0")
    latency_ms = Column(Integer, nullable=False, default=0, server_default="0")
    status = Column(String(16), nullable=False, index=True)
    error_code = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
