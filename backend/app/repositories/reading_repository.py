from datetime import date, datetime

from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.sensor_reading import SensorReading


class ReadingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, city_id: int, temperature: float, humidity: float,
               pm25: float, pm10: float, ozone: float,
               carbon_monoxide: float, wind_speed: float,
               uv_index: float = 0.0) -> SensorReading:
        try:
            reading = SensorReading(
                city_id=city_id,
                temperature=temperature,
                humidity=humidity,
                pm25=pm25,
                pm10=pm10,
                ozone=ozone,
                carbon_monoxide=carbon_monoxide,
                wind_speed=wind_speed,
                uv_index=uv_index,
            )
            self.db.add(reading)
            self.db.commit()
            self.db.refresh(reading)
            logger.info("Reading created for city_id=%s", city_id)
            return reading
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create reading: %s", e)
            raise DatabaseException("Failed to create reading", e)

    def get_latest_per_city(self) -> list[SensorReading]:
        try:
            sub = (
                self.db.query(
                    SensorReading.city_id,
                    SensorReading.id,
                )
                .distinct(SensorReading.city_id)
                .order_by(SensorReading.city_id, SensorReading.created_at.desc())
                .subquery()
            )
            return self.db.query(SensorReading).join(
                sub, SensorReading.id == sub.c.id
            ).all()
        except Exception as e:
            logger.error("Failed to fetch latest readings: %s", e)
            raise DatabaseException("Failed to fetch latest readings", e)

    def get_history(self, city_id: int | None = None,
                    start_date: date | None = None,
                    end_date: date | None = None) -> list[SensorReading]:
        try:
            query = self.db.query(SensorReading)
            if city_id:
                query = query.filter(SensorReading.city_id == city_id)
            if start_date:
                query = query.filter(SensorReading.created_at >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                query = query.filter(SensorReading.created_at <= datetime.combine(end_date, datetime.max.time()))
            return query.order_by(SensorReading.created_at.desc()).limit(500).all()
        except Exception as e:
            logger.error("Failed to fetch history: %s", e)
            raise DatabaseException("Failed to fetch reading history", e)
