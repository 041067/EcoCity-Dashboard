from __future__ import annotations

from app.services.esg_data.normalization_service import CATALOG, NormalizedIndicator


class ClimateRiskService:
    """Explicit, deterministic climate thresholds. This service never uses generative AI."""

    LEVELS = {1: "low", 2: "moderate", 3: "high", 4: "critical"}

    @staticmethod
    def _level(value: float, moderate: float, high: float, critical: float) -> int:
        if value >= critical:
            return 4
        if value >= high:
            return 3
        if value >= moderate:
            return 2
        return 1

    def derive(self, values: list[NormalizedIndicator]) -> list[NormalizedIndicator]:
        source = {item.definition.code: item for item in values}
        temperature = source.get("CLIMATE_TEMPERATURE")
        precipitation = source.get("CLIMATE_PRECIPITATION")
        wind = source.get("CLIMATE_WIND_SPEED")
        et0 = source.get("WATER_EVAPOTRANSPIRATION")
        risks: list[tuple[str, int, str]] = []
        if temperature:
            risks.append(("CLIMATE_HEAT_RISK", self._level(temperature.value, 30, 35, 40), "temperature"))
        if precipitation:
            risks.append(("CLIMATE_FLOOD_RISK", self._level(precipitation.value, 10, 25, 50), "precipitation"))
            drought_level = 1
            if precipitation.value < 1:
                drought_level = 2
            if precipitation.value < 0.2 and et0 and et0.value >= 4:
                drought_level = 3
            if precipitation.value == 0 and et0 and et0.value >= 6:
                drought_level = 4
            risks.extend([
                ("WATER_DROUGHT_RISK", drought_level, "precipitation_et0"),
                ("WATER_STRESS_SIGNAL", drought_level, "precipitation_et0"),
            ])
        if wind:
            risks.append(("CLIMATE_WIND_RISK", self._level(wind.value, 40, 65, 90), "wind_speed"))
        observed_at = max((item.observed_at for item in values if item.observed_at), default=None)
        return [
            NormalizedIndicator(
                definition=CATALOG[code],
                value=float(level),
                source="climate_risk_engine",
                source_reference="EcoCity deterministic climate thresholds v1",
                observed_at=observed_at,
                metadata={"risk_level": self.LEVELS[level], "rule_input": rule, "methodology": "thresholds_v1"},
                quality_score=100.0,
                relevance_score=95.0,
            )
            for code, level, rule in risks
        ]
