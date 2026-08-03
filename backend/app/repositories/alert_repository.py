from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.alert import Alert


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, city_id: int, severity: str, title: str, description: str) -> Alert:
        try:
            alert = Alert(
                city_id=city_id,
                severity=severity,
                title=title,
                description=description,
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            logger.info("Alert created for city_id=%s: %s", city_id, title)
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create alert: %s", e)
            raise DatabaseException("Failed to create alert", e)

    def list_all(self, limit: int = 100) -> list[Alert]:
        try:
            return (
                self.db.query(Alert)
                .order_by(Alert.created_at.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error("Failed to fetch alerts: %s", e)
            raise DatabaseException("Failed to fetch alerts", e)

    def list_by_city(self, city_id: int, limit: int = 50) -> list[Alert]:
        try:
            return (
                self.db.query(Alert)
                .filter(Alert.city_id == city_id)
                .order_by(Alert.created_at.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error("Failed to fetch alerts for city %s: %s", city_id, e)
            raise DatabaseException(f"Failed to fetch alerts for city {city_id}", e)
