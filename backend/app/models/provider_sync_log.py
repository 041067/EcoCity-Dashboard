from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database.session import Base


class ProviderSyncLog(Base):
    """Small operational audit log for provider availability, cache use and latency."""

    __tablename__ = "provider_sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(80), nullable=False, index=True)
    site_id = Column(Integer, nullable=True, index=True)
    status = Column(String(24), nullable=False, index=True)
    data_category = Column(String(80), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
