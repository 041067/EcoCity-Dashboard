from app.clients.groq_client import GroqClient
from app.logs.logger import logger
from app.repositories.ai_report_repository import AIReportRepository
from app.repositories.reading_repository import ReadingRepository


class AIService:
    def __init__(self, report_repo: AIReportRepository, reading_repo: ReadingRepository) -> None:
        self.client = GroqClient()
        self.report_repo = report_repo
        self.reading_repo = reading_repo

    def generate_report(self, city_id: int, city_name: str) -> dict:
        readings = self.reading_repo.get_history(city_id=city_id, limit=10)

        if not readings:
            logger.warning("No readings available for city %s", city_name)
            return {"city": city_name, "summary": "No data available", "recommendation": ""}

        latest = readings[0]
        prompt = (
            f"City: {city_name}\n"
            f"Temperature: {latest.temperature}°C\n"
            f"Humidity: {latest.humidity}%\n"
            f"PM2.5: {latest.pm25} µg/m³\n"
            f"PM10: {latest.pm10} µg/m³\n"
            f"Ozone: {latest.ozone} µg/m³\n"
            f"CO: {latest.carbon_monoxide} µg/m³\n"
            f"Wind: {latest.wind_speed} km/h\n\n"
            "Provide a short environmental summary and recommendation in Portuguese."
        )

        content = self.client.generate_insight(prompt)

        parts = content.split("\n", 1)
        summary = parts[0] if parts else content
        recommendation = parts[1] if len(parts) > 1 else ""

        report = self.report_repo.create(city_id=city_id, summary=summary, recommendation=recommendation)
        return {"city": city_name, "summary": report.summary, "recommendation": report.recommendation}
