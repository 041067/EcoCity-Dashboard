from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func

from app.database.session import Base


class ESGReport(Base):
    """A versioned, structured AI interpretation of deterministic ESG data."""

    __tablename__ = "esg_reports"
    __table_args__ = (
        CheckConstraint(
            "report_type IN ('executive', 'materiality', 'risk', 'progress', 'full_esg')",
            name="ck_esg_reports_type",
        ),
        CheckConstraint(
            "status IN ('completed', 'failed')", name="ck_esg_reports_status"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    report_type = Column(String(24), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)
    status = Column(String(16), nullable=False, default="completed", server_default="completed")
    content = Column(JSON, nullable=False)
    data_sufficiency = Column(JSON, nullable=False)
    context_hash = Column(String(64), nullable=False, index=True)
    model = Column(String(120), nullable=False)
    prompt_version = Column(String(80), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
