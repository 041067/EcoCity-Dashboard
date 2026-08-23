from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class ESGTopic(Base):
    __tablename__ = "esg_topics"
    __table_args__ = (CheckConstraint("pillar IN ('E', 'S', 'G')", name="ck_esg_topics_pillar"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(80), nullable=False, unique=True)
    name = Column(String(160), nullable=False)
    pillar = Column(String(1), nullable=False, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization_links = relationship("OrganizationESGTopic", back_populates="topic")
    materiality_assessments = relationship("MaterialityAssessment", back_populates="topic")
