from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class AuditEntry(Base):
    """Append-only mutation history. It is only created by server-side services."""

    __tablename__ = "audit_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    actor = Column(String(120), nullable=False, default="system", server_default="system")
    entity_type = Column(String(80), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    action = Column(String(80), nullable=False, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    source = Column(String(120), nullable=False, default="api", server_default="api")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    organization = relationship("Organization", back_populates="audit_entries")
