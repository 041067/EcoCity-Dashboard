from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class Stakeholder(Base):
    __tablename__ = "stakeholders"
    __table_args__ = (
        CheckConstraint(
            "stakeholder_type IN ('employees', 'customers', 'suppliers', 'investors', 'government', "
            "'community', 'environment', 'partners', 'other')",
            name="ck_stakeholders_type",
        ),
        CheckConstraint("influence_level BETWEEN 1 AND 5", name="ck_stakeholders_influence"),
        CheckConstraint("impact_level BETWEEN 1 AND 5", name="ck_stakeholders_impact"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False)
    stakeholder_type = Column(String(30), nullable=False)
    influence_level = Column(Integer, nullable=False)
    impact_level = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="stakeholders")
    materiality_assessments = relationship("StakeholderAssessment", back_populates="stakeholder")
