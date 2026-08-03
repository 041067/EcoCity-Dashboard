from typing import Any

from app.logs.logger import logger
from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.utils.air_quality import compute_aqi


class AlertService:
    """Avalia leituras recentes e cria alertas inteligentes."""

    def __init__(self, alert_repo: AlertRepository) -> None:
        self.alert_repo = alert_repo

    def evaluate_reading(self, city_id: int, reading: Any | dict) -> list[Alert]:
        """Gere as regras a partir de uma leitura (modelo ou dict) e persiste os alertas."""
        data = self._as_dict(reading)
        rules = self._build_rules(data)
        alerts: list[Alert] = []
        for severity, title, description in rules:
            alert = self.alert_repo.create(
                city_id=city_id,
                severity=severity,
                title=title,
                description=description,
            )
            alerts.append(alert)
            logger.info("Alert created: %s: %s", severity, title)
        return alerts

    def _build_rules(self, data: dict) -> list[tuple[str, str, str]]:
        pm25 = float(data.get("pm25", 0.0))
        aqi = int(data.get("aqi", compute_aqi(pm25)))
        temperature = float(data.get("temperature", 0.0))
        humidity = float(data.get("humidity", 0.0))
        wind_speed = float(data.get("wind_speed", 0.0))
        uv_index = float(data.get("uv_index", 0.0))

        rules: list[tuple[str, str, str]] = []
        if aqi > 100:
            rules.append((
                "danger",
                "Qualidade do ar ruim",
                f"O AQI de {aqi} indica qualidade do ar prejudicial à saúde.",
            ))
        if temperature > 38:
            rules.append((
                "danger",
                "Temperatura extrema",
                f"Temperatura de {temperature:.1f}°C acima do limite seguro.",
            ))
        if temperature > 33:
            rules.append((
                "warning",
                "Temperatura alta",
                f"Temperatura de {temperature:.1f}°C exige cuidados com a saúde.",
            ))
        if humidity > 90:
            rules.append((
                "warning",
                "Umidade elevada",
                f"Umidade relativa de {humidity:.0f}% acima do confortável.",
            ))
        if wind_speed > 60:
            rules.append((
                "warning",
                "Ventos fortes",
                f"Vento a {wind_speed:.0f} km/h requer atenção.",
            ))
        if uv_index >= 8:
            rules.append((
                "danger",
                "Raios UV extremos",
                f"Índice UV de {uv_index:.1f} exige proteção solar máxima.",
            ))
        return rules

    @staticmethod
    def _as_dict(reading: Any | dict) -> dict:
        if isinstance(reading, dict):
            return reading
        return {
            "temperature": getattr(reading, "temperature", 0.0),
            "humidity": getattr(reading, "humidity", 0.0),
            "pm25": getattr(reading, "pm25", 0.0),
            "wind_speed": getattr(reading, "wind_speed", 0.0),
            "uv_index": getattr(reading, "uv_index", 0.0),
        }
