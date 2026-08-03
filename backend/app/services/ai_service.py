from datetime import datetime, timedelta

from app.clients.groq_client import GroqClient
from app.logs.logger import logger
from app.repositories.ai_report_repository import AIReportRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.reading_repository import ReadingRepository
from app.utils.air_quality import compute_aqi


class AIService:
    """Gera relatórios ambientais e respostas conversacionais via Groq."""

    REPORT_PROMPT = (
        "Você é um especialista em meio ambiente. Analise os dados climáticos e de "
        "qualidade do ar das últimas 24 horas de {city} e escreva um relatório em "
        "português com exatamente 4 parágrafos cobrindo, nesta ordem:\n"
        "1. Situação ambiental atual\n"
        "2. Riscos para a população\n"
        "3. Tendência observada\n"
        "4. Recomendações para a prefeitura\n\n"
        "Dados das últimas 24 horas:\n{data}\n\n"
        "Alertas ativos da cidade:\n{alerts}\n\n"
        "Seja objetivo, técnico e direto. Não use títulos, apenas parágrafos."
    )

    CHAT_PROMPT = (
        "Você é o assistente ambiental do EcoCity Dashboard. Responda em português "
        "usando APENAS os dados abaixo, de forma curta e objetiva (máximo 5 linhas). "
        "Se a pergunta não puder ser respondida com os dados, diga que não há dados suficientes.\n\n"
        "Pergunta do usuário: {question}\n\n"
        "Dados atuais das cidades monitoradas:\n{data}"
    )

    def __init__(self, report_repo: AIReportRepository, reading_repo: ReadingRepository,
                 alert_repo: AlertRepository) -> None:
        self.client = GroqClient()
        self.report_repo = report_repo
        self.reading_repo = reading_repo
        self.alert_repo = alert_repo

    def generate_report(self, city_id: int, city_name: str) -> dict:
        readings = self.reading_repo.get_history(city_id=city_id, start_date=datetime.now() - timedelta(hours=24))
        readings = sorted(readings, key=lambda r: r.created_at) if readings else []

        if not readings:
            logger.warning("No readings available for city %s", city_name)
            return {
                "city": city_name,
                "summary": "Sem dados disponíveis nas últimas 24 horas para esta cidade.",
                "recommendation": "",
                "created_at": None,
            }

        data_str = self._format_readings(readings)
        alerts_str = self._format_alerts(city_id)

        prompt = self.REPORT_PROMPT.format(city=city_name, data=data_str, alerts=alerts_str)
        content = self.client.generate_insight(prompt)

        parts = content.split("\n", 1)
        summary = parts[0] if parts else content
        recommendation = parts[1] if len(parts) > 1 else ""

        report = self.report_repo.create(city_id=city_id, summary=summary, recommendation=recommendation)
        return {
            "city": city_name,
            "summary": report.summary,
            "recommendation": report.recommendation,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }

    def get_latest_report(self, city_id: int) -> dict | None:
        report = self.report_repo.get_latest_by_city(city_id)
        if not report:
            return None
        return {
            "city_id": report.city_id,
            "summary": report.summary,
            "recommendation": report.recommendation,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }

    def chat(self, question: str) -> str:
        readings = self.reading_repo.get_latest_per_city()
        data_str = self._format_latest(readings)
        prompt = self.CHAT_PROMPT.format(question=question, data=data_str)
        return self.client.generate_insight(prompt)

    def _format_readings(self, readings) -> str:
        lines = []
        for r in readings:
            lines.append(
                f"- {r.created_at.isoformat() if r.created_at else '?'}: "
                f"temp {r.temperature:.1f}°C, umid {r.humidity:.0f}%, "
                f"vento {r.wind_speed:.1f} km/h, PM2.5 {r.pm25:.1f}, "
                f"PM10 {r.pm10:.1f}, ozônio {r.ozone:.1f}, CO {r.carbon_monoxide:.1f}, "
                f"UV {r.uv_index}."
            )
        return "\n".join(lines) if lines else "Nenhuma leitura."

    def _format_latest(self, readings) -> str:
        lines = []
        for r in readings:
            lines.append(
                f"- Cidade {r.name if hasattr(r, 'name') else r.city_id}: "
                f"temp {r.temperature:.1f}°C, umid {r.humidity:.0f}%, "
                f"vento {r.wind_speed:.1f} km/h, PM2.5 {r.pm25:.1f} "
                f"(AQI {compute_aqi(r.pm25)}), UV {r.uv_index}."
            )
        return "\n".join(lines) if lines else "Nenhuma leitura disponível."

    def _format_alerts(self, city_id: int) -> str:
        alerts = self.alert_repo.list_by_city(city_id, limit=5)
        if not alerts:
            return "Nenhum alerta ativo."
        return "\n".join(f"- [{a.severity}] {a.title}: {a.description}" for a in alerts)
