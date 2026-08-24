from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class ESGIndicator(Base):
    """Canonical definition of a measurable ESG signal, independent of its provider."""

    __tablename__ = "esg_indicators"
    __table_args__ = (
        CheckConstraint("pillar IN ('E', 'S', 'G')", name="ck_esg_indicators_pillar"),
        UniqueConstraint("code"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    pillar = Column(String(1), nullable=False, default="E", server_default="E")
    category = Column(String(80), nullable=False, index=True)
    unit = Column(String(40), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(30), nullable=False, default="external", server_default="external")
    direction = Column(
        String(24), nullable=False, default="higher_is_better", server_default="higher_is_better"
    )
    active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    values = relationship("IndicatorValue", back_populates="indicator")
    targets = relationship("ESGTarget", back_populates="indicator")
    gaps = relationship("ESGGap", back_populates="indicator")
    opportunities = relationship("ESGOpportunity", back_populates="indicator")
