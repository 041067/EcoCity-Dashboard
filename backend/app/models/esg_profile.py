from sqlalchemy import (
    Boolean,
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


class ESGProfile(Base):
    __tablename__ = "esg_profiles"
    __table_args__ = (
        CheckConstraint(
            "esg_maturity_level IN ('initial', 'developing', 'structured', 'advanced')",
            name="ck_esg_profiles_maturity",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    reporting_year = Column(Integer, nullable=False)
    environmental_enabled = Column(Boolean, nullable=False, default=True, server_default="1")
    social_enabled = Column(Boolean, nullable=False, default=True, server_default="1")
    governance_enabled = Column(Boolean, nullable=False, default=True, server_default="1")
    sustainability_strategy = Column(Text, nullable=True)
    esg_maturity_level = Column(String(20), nullable=False, default="initial", server_default="initial")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="esg_profile")
