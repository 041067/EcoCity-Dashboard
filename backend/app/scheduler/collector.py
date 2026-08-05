from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database.session import SessionLocal
from app.logs.logger import logger
from app.repositories.alert_repository import AlertRepository
from app.repositories.city_repository import CityRepository
from app.repositories.reading_repository import ReadingRepository
from app.services.alert_service import AlertService
from app.services.score_service import ScoreService
from app.services.weather_service import WeatherService

COLLECT_INTERVAL_MINUTES = 15


class Collector:
    """Coleta automática de dados climáticos + avaliação de alertas."""

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

    def collect_job(self) -> None:
        try:
            with SessionLocal() as db:
                city_repo = CityRepository(db)
                reading_repo = ReadingRepository(db)
                weather = WeatherService(city_repo, reading_repo)
                results = weather.collect_all()

                alert_repo = AlertRepository(db)
                alert_service = AlertService(alert_repo)
                score_service = ScoreService()
                for r in reading_repo.get_latest_per_city():
                    aqi = score_service.aqi_from_readings(r.pm25)
                    alert_service.evaluate_reading(
                        r.city_id,
                        {
                            "temperature": r.temperature,
                            "humidity": r.humidity,
                            "pm25": r.pm25,
                            "wind_speed": r.wind_speed,
                            "uv_index": r.uv_index,
                            "aqi": aqi,
                        },
                    )

            logger.info("Collector job finished at %s (%s cities)", datetime.now().isoformat(), len(results))
        except Exception as e:
            logger.error("Collector job failed: %s", e)

    def start(self) -> None:
        if self.scheduler.running:
            return
        try:
            self.scheduler.add_job(
                self.collect_job,
                trigger=IntervalTrigger(minutes=COLLECT_INTERVAL_MINUTES),
                id="collector_15min",
                replace_existing=True,
            )
            self.scheduler.start()
            logger.info("Scheduler started: collect every %s minutes", COLLECT_INTERVAL_MINUTES)
        except Exception as e:
            logger.error("Failed to start scheduler: %s", e)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")


collector = Collector()
