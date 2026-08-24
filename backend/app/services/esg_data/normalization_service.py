from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    category: str
    unit: str
    description: str
    source_type: str = "external"
    pillar: str = "E"


@dataclass(frozen=True)
class NormalizedIndicator:
    definition: IndicatorDefinition
    value: float
    source: str
    source_reference: str
    observed_at: datetime | None
    metadata: dict[str, Any]
    quality_score: float
    relevance_score: float


CATALOG: dict[str, IndicatorDefinition] = {
    "CLIMATE_TEMPERATURE": IndicatorDefinition("CLIMATE_TEMPERATURE", "Temperatura", "climate", "°C", "Temperatura do ar observada ou modelada."),
    "CLIMATE_HUMIDITY": IndicatorDefinition("CLIMATE_HUMIDITY", "Umidade relativa", "climate", "%", "Umidade relativa do ar."),
    "CLIMATE_PRECIPITATION": IndicatorDefinition("CLIMATE_PRECIPITATION", "Precipitação", "climate", "mm", "Precipitação no período observado."),
    "CLIMATE_WIND_SPEED": IndicatorDefinition("CLIMATE_WIND_SPEED", "Velocidade do vento", "climate", "km/h", "Velocidade do vento a 10 metros."),
    "ENERGY_SOLAR_RADIATION": IndicatorDefinition("ENERGY_SOLAR_RADIATION", "Radiação solar", "energy", "W/m²", "Radiação solar de onda curta atual."),
    "ENERGY_DIRECT_RADIATION": IndicatorDefinition("ENERGY_DIRECT_RADIATION", "Radiação solar direta", "energy", "W/m²", "Componente direto da radiação solar."),
    "ENERGY_DIFFUSE_RADIATION": IndicatorDefinition("ENERGY_DIFFUSE_RADIATION", "Radiação solar difusa", "energy", "W/m²", "Componente difuso da radiação solar."),
    "ENERGY_SUNSHINE_DURATION": IndicatorDefinition("ENERGY_SUNSHINE_DURATION", "Duração do brilho solar", "energy", "h", "Duração diária de insolação."),
    "ENERGY_SOLAR_POTENTIAL": IndicatorDefinition("ENERGY_SOLAR_POTENTIAL", "Potencial solar histórico", "energy", "kWh/m²/dia", "Média climatológica diária de irradiação solar."),
    "WATER_SOIL_MOISTURE": IndicatorDefinition("WATER_SOIL_MOISTURE", "Umidade do solo", "water", "m³/m³", "Umidade volumétrica da camada superficial do solo."),
    "WATER_EVAPOTRANSPIRATION": IndicatorDefinition("WATER_EVAPOTRANSPIRATION", "Evapotranspiração de referência", "water", "mm", "Evapotranspiração de referência FAO."),
    "AIR_PM25": IndicatorDefinition("AIR_PM25", "Material particulado PM2.5", "air", "µg/m³", "Concentração de partículas finas PM2.5."),
    "AIR_PM10": IndicatorDefinition("AIR_PM10", "Material particulado PM10", "air", "µg/m³", "Concentração de partículas PM10."),
    "AIR_NO2": IndicatorDefinition("AIR_NO2", "Dióxido de nitrogênio", "air", "µg/m³", "Concentração de NO₂."),
    "AIR_O3": IndicatorDefinition("AIR_O3", "Ozônio", "air", "µg/m³", "Concentração de ozônio."),
    "AIR_SO2": IndicatorDefinition("AIR_SO2", "Dióxido de enxofre", "air", "µg/m³", "Concentração de SO₂."),
    "AIR_CO": IndicatorDefinition("AIR_CO", "Monóxido de carbono", "air", "µg/m³", "Concentração de CO."),
    "CLIMATE_BASELINE_TEMPERATURE": IndicatorDefinition("CLIMATE_BASELINE_TEMPERATURE", "Temperatura climatológica", "climate", "°C", "Linha de base climatológica histórica."),
    "CLIMATE_BASELINE_PRECIPITATION": IndicatorDefinition("CLIMATE_BASELINE_PRECIPITATION", "Precipitação climatológica", "climate", "mm/dia", "Linha de base histórica de precipitação."),
    "FOREST_FIRE_ALERTS": IndicatorDefinition("FOREST_FIRE_ALERTS", "Alertas de queimadas", "territory", "alertas", "Alertas de focos de calor no raio configurado."),
    "TERRITORY_DEFORESTATION_ALERTS": IndicatorDefinition("TERRITORY_DEFORESTATION_ALERTS", "Alertas de desmatamento", "territory", "alertas", "Alertas de desmatamento no raio configurado."),
    "ENERGY_RENEWABLE_SHARE": IndicatorDefinition("ENERGY_RENEWABLE_SHARE", "Participação renovável", "energy", "%", "Participação de fontes renováveis no contexto elétrico."),
    "ENERGY_GENERATION": IndicatorDefinition("ENERGY_GENERATION", "Geração de energia", "energy", "MW", "Geração elétrica reportada pela fonte."),
    "CLIMATE_HEAT_RISK": IndicatorDefinition("CLIMATE_HEAT_RISK", "Risco de calor", "risk", "índice", "Risco determinístico de calor.", "derived"),
    "WATER_DROUGHT_RISK": IndicatorDefinition("WATER_DROUGHT_RISK", "Risco de seca", "risk", "índice", "Risco determinístico de seca.", "derived"),
    "CLIMATE_FLOOD_RISK": IndicatorDefinition("CLIMATE_FLOOD_RISK", "Risco de inundação", "risk", "índice", "Risco determinístico de inundação.", "derived"),
    "CLIMATE_WIND_RISK": IndicatorDefinition("CLIMATE_WIND_RISK", "Risco de vento", "risk", "índice", "Risco determinístico de vento.", "derived"),
    "WATER_STRESS_SIGNAL": IndicatorDefinition("WATER_STRESS_SIGNAL", "Sinal de estresse hídrico", "risk", "índice", "Sinal determinístico de estresse hídrico.", "derived"),
}


class NormalizationService:
    """Turns provider-specific payloads into the canonical ESG indicator vocabulary."""

    PROVIDER_QUALITY = {"open_meteo": 78.0, "openaq": 90.0, "nasa_power": 88.0, "inpe": 88.0, "aneel": 85.0}

    def normalize(self, provider: str, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        handlers = {
            "open_meteo": self._open_meteo,
            "openaq": self._openaq,
            "nasa_power": self._nasa_power,
            "inpe": self._inpe,
            "aneel": self._aneel,
        }
        return handlers[provider](payload)

    def _item(
        self,
        code: str,
        value: Any,
        provider: str,
        reference: str,
        observed_at: datetime | None,
        metadata: dict[str, Any],
        unit: str | None = None,
    ) -> NormalizedIndicator | None:
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if not isfinite(number):
            return None
        definition = CATALOG[code]
        if unit and unit != definition.unit:
            return None
        return NormalizedIndicator(
            definition=definition,
            value=number,
            source=provider,
            source_reference=reference,
            observed_at=observed_at,
            metadata=metadata,
            quality_score=self.PROVIDER_QUALITY.get(provider, 75.0),
            relevance_score=95.0 if definition.category in {"risk", "air", "water"} else 85.0,
        )

    @staticmethod
    def _observed(value: Any) -> datetime | None:
        if isinstance(value, dict):
            value = value.get("utc") or value.get("local")
        if not value or not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return None

    def _open_meteo(self, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        channel = payload.get("channel", "climate")
        raw = payload.get("payload", payload)
        current = raw.get("current", {}) if isinstance(raw, dict) else {}
        if not isinstance(current, dict):
            return []
        observed_at = self._observed(current.get("time"))
        reference = "https://open-meteo.com/"
        metadata = {"channel": channel, "units": raw.get("current_units", {})}
        climate_map = {
            "temperature_2m": "CLIMATE_TEMPERATURE",
            "relative_humidity_2m": "CLIMATE_HUMIDITY",
            "precipitation": "CLIMATE_PRECIPITATION",
            "wind_speed_10m": "CLIMATE_WIND_SPEED",
            "shortwave_radiation": "ENERGY_SOLAR_RADIATION",
            "direct_radiation": "ENERGY_DIRECT_RADIATION",
            "diffuse_radiation": "ENERGY_DIFFUSE_RADIATION",
            "soil_moisture_0_to_1cm": "WATER_SOIL_MOISTURE",
            "et0_fao_evapotranspiration": "WATER_EVAPOTRANSPIRATION",
            "pm2_5": "AIR_PM25",
            "pm10": "AIR_PM10",
            "nitrogen_dioxide": "AIR_NO2",
            "ozone": "AIR_O3",
            "sulphur_dioxide": "AIR_SO2",
            "carbon_monoxide": "AIR_CO",
        }
        items = [
            item
            for field, code in climate_map.items()
            if (item := self._item(code, current.get(field), "open_meteo", reference, observed_at, metadata))
            is not None
        ]
        daily = raw.get("daily", {}) if isinstance(raw, dict) else {}
        sunshine = daily.get("sunshine_duration", []) if isinstance(daily, dict) else []
        if isinstance(sunshine, list) and sunshine:
            item = self._item(
                "ENERGY_SUNSHINE_DURATION",
                float(sunshine[0]) / 3600,
                "open_meteo",
                reference,
                observed_at,
                metadata,
            )
            if item:
                items.append(item)
        return items

    def _openaq(self, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        raw = payload.get("payload", payload)
        results = raw.get("results", []) if isinstance(raw, dict) else []
        parameter_codes = {"pm25": "AIR_PM25", "pm2.5": "AIR_PM25", "pm10": "AIR_PM10", "no2": "AIR_NO2", "o3": "AIR_O3", "so2": "AIR_SO2", "co": "AIR_CO"}
        items: list[NormalizedIndicator] = []
        for result in results if isinstance(results, list) else []:
            measurements = result.get("measurements", result.get("sensors", [])) if isinstance(result, dict) else []
            if isinstance(result, dict) and "value" in result:
                measurements = [result]
            for measurement in measurements if isinstance(measurements, list) else []:
                if not isinstance(measurement, dict):
                    continue
                parameter = measurement.get("parameter", measurement.get("name", ""))
                if isinstance(parameter, dict):
                    parameter = parameter.get("name", parameter.get("id", ""))
                code = parameter_codes.get(str(parameter).lower())
                if not code:
                    continue
                value = measurement.get("value", measurement.get("lastValue"))
                observed = self._observed(measurement.get("datetime", measurement.get("lastUpdated")))
                item = self._item(code, value, "openaq", "https://openaq.org/", observed, {"measurement": measurement})
                if item:
                    items.append(item)
        return items

    def _nasa_power(self, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        raw = payload.get("payload", payload)
        parameters = raw.get("properties", {}).get("parameter", {}) if isinstance(raw, dict) else {}
        if not isinstance(parameters, dict):
            return []
        def annual(name: str) -> Any:
            values = parameters.get(name, {})
            if not isinstance(values, dict):
                return None
            annual_value = values.get("ANN") or values.get("annual")
            if annual_value is not None:
                return annual_value
            numbers = [float(value) for value in values.values() if isinstance(value, int | float) and value > -900]
            return sum(numbers) / len(numbers) if numbers else None
        reference = "https://power.larc.nasa.gov/"
        return [
            item
            for code, value in (
                ("ENERGY_SOLAR_POTENTIAL", annual("ALLSKY_SFC_SW_DWN")),
                ("CLIMATE_BASELINE_TEMPERATURE", annual("T2M")),
                ("CLIMATE_BASELINE_PRECIPITATION", annual("PRECTOTCORR")),
            )
            if (item := self._item(code, value, "nasa_power", reference, None, {"period": "climatology"})) is not None
        ]

    def _inpe(self, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        raw = payload.get("payload", payload)
        if not isinstance(raw, dict):
            return []
        return [
            item
            for code, value in (
                ("FOREST_FIRE_ALERTS", raw.get("fire_alerts", raw.get("fires"))),
                ("TERRITORY_DEFORESTATION_ALERTS", raw.get("deforestation_alerts", raw.get("deforestation"))),
            )
            if (item := self._item(code, value, "inpe", "INPE configured endpoint", self._observed(raw.get("observed_at")), {"radius_km": raw.get("radius_km", 10)})) is not None
        ]

    def _aneel(self, payload: dict[str, Any]) -> list[NormalizedIndicator]:
        raw = payload.get("payload", payload)
        if not isinstance(raw, dict):
            return []
        return [
            item
            for code, value in (
                ("ENERGY_RENEWABLE_SHARE", raw.get("renewable_share")),
                ("ENERGY_GENERATION", raw.get("generation_mw")),
            )
            if (item := self._item(code, value, "aneel", "ANEEL configured endpoint", self._observed(raw.get("observed_at")), {"dataset": raw.get("dataset")})) is not None
        ]
