from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.ai_report import AIReport


class AIReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, city_id: int, summary: str, recommendation: str) -> AIReport:
        try:
            report = AIReport(
                city_id=city_id,
                summary=summary,
                recommendation=recommendation,
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            logger.info("AIReport created for city_id=%s", city_id)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create AI report: %s", e)
            raise DatabaseException("Failed to create AI report", e)

    def get_latest_by_city(self, city_id: int) -> AIReport | None:
        try:
            return (
                self.db.query(AIReport)
                .filter(AIReport.city_id == city_id)
                .order_by(AIReport.created_at.desc())
                .first()
            )
        except Exception as e:
            logger.error("Failed to fetch latest report for city %s: %s", city_id, e)
            raise DatabaseException(f"Failed to fetch report for city {city_id}", e)
