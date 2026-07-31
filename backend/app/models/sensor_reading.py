from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, func

from app.database.session import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pm25 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=False)
    ozone = Column(Float, nullable=False)
    carbon_monoxide = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
