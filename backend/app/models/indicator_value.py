from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class IndicatorValue(Base):
    """An immutable, provenance-rich observation and the database-backed provider cache."""

    __tablename__ = "indicator_values"
    __table_args__ = (
        CheckConstraint("quality_score BETWEEN 0 AND 100", name="ck_indicator_values_quality"),
        CheckConstraint("freshness_score BETWEEN 0 AND 100", name="ck_indicator_values_freshness"),
        CheckConstraint("relevance_score BETWEEN 0 AND 100", name="ck_indicator_values_relevance"),
        CheckConstraint("confidence_score BETWEEN 0 AND 100", name="ck_indicator_values_confidence"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, ForeignKey("esg_indicators.id", ondelete="RESTRICT"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)
    source = Column(String(80), nullable=False, index=True)
    source_reference = Column(String(1000), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    observed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    source_metadata = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=False, default=75.0, server_default="75")
    freshness_score = Column(Float, nullable=False, default=100.0, server_default="100")
    relevance_score = Column(Float, nullable=False, default=85.0, server_default="85")
    confidence_score = Column(Float, nullable=False, default=80.0, server_default="80")

    indicator = relationship("ESGIndicator", back_populates="values")
    organization = relationship("Organization", back_populates="indicator_values")
    site = relationship("Site", back_populates="indicator_values")
    materiality_evidences = relationship("MaterialityEvidence", back_populates="indicator_value")
    risks = relationship("ESGRisk", back_populates="indicator_value")
    opportunities = relationship("ESGOpportunity", back_populates="indicator_value")
