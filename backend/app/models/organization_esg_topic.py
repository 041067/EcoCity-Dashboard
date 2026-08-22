from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class OrganizationESGTopic(Base):
    __tablename__ = "organization_esg_topics"
    __table_args__ = (
        UniqueConstraint("organization_id", "topic_id", name="uq_organization_esg_topics_organization_topic"),
        CheckConstraint("priority BETWEEN 1 AND 5", name="ck_organization_esg_topics_priority"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id = Column(Integer, ForeignKey("esg_topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=True, server_default="1")
    priority = Column(Integer, nullable=False, default=3, server_default="3")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="esg_topic_links")
    topic = relationship("ESGTopic", back_populates="organization_links")
