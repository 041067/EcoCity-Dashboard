from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class Site(Base):
    __tablename__ = "sites"
    __table_args__ = (
        CheckConstraint(
            "site_type IN ('headquarters', 'factory', 'warehouse', 'office', 'municipal_region', 'other')",
            name="ck_sites_type",
        ),
        CheckConstraint("employee_count IS NULL OR employee_count >= 0", name="ck_sites_employee_count"),
        CheckConstraint("area_m2 IS NULL OR area_m2 >= 0", name="ck_sites_area_m2"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False)
    site_type = Column(String(30), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True)
    employee_count = Column(Integer, nullable=True)
    area_m2 = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="sites")
    city = relationship("City")
    indicator_values = relationship("IndicatorValue", back_populates="site", cascade="all, delete-orphan")
    targets = relationship("ESGTarget", back_populates="site")
    gaps = relationship("ESGGap", back_populates="site")
    risks = relationship("ESGRisk", back_populates="site")
    opportunities = relationship("ESGOpportunity", back_populates="site")
    action_plans = relationship("ActionPlan", back_populates="site")
