from datetime import UTC, datetime

import httpx

from app.clients.provider_http import get_json
from app.core.config import settings
from app.exceptions.external_api_exception import ExternalApiException
from app.logs.logger import logger


class OpenMeteoClient:
    WEATHER_URL = f"{settings.OPEN_METEO_URL}/forecast"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(self) -> None:
        self.base_url = settings.OPEN_METEO_URL

    def get_weather(self, latitude: float, longitude: float) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index",
            "timezone": "auto",
        }
        try:
            response = httpx.get(self.WEATHER_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.info("Weather data fetched for lat=%s lon=%s", latitude, longitude)
            return data["current"]
        except httpx.HTTPStatusError as e:
            raise ExternalApiException("Open-Meteo", "HTTP error", e.response.status_code)
        except httpx.TimeoutException:
            raise ExternalApiException("Open-Meteo", "Request timed out", 408)
        except Exception as e:
            raise ExternalApiException("Open-Meteo", str(e))

    def get_air_quality(self, latitude: float, longitude: float) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "pm2_5,pm10,ozone,carbon_monoxide",
            "timezone": "auto",
        }
        try:
            response = httpx.get(self.AIR_QUALITY_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.info("Air quality data fetched for lat=%s lon=%s", latitude, longitude)
            return data["current"]
        except httpx.HTTPStatusError as e:
            raise ExternalApiException("Open-Meteo", "Air quality HTTP error", e.response.status_code)
        except httpx.TimeoutException:
            raise ExternalApiException("Open-Meteo", "Air quality request timed out", 408)
        except Exception as e:
            raise ExternalApiException("Open-Meteo", str(e))

    def get_intelligence_climate(self, latitude: float, longitude: float) -> dict:
        """Richer current climate and energy payload used only by Sprint 8 providers."""
        data, duration_ms = get_json(
            "open_meteo",
            self.WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "hourly": "shortwave_radiation,direct_radiation,diffuse_radiation,et0_fao_evapotranspiration,soil_moisture_0_to_1cm",
                "daily": "sunshine_duration",
                "timezone": "UTC",
                "wind_speed_unit": "kmh",
            },
        )
        current = data.get("current")
        hourly = data.get("hourly")
        if isinstance(current, dict) and isinstance(hourly, dict):
            current_time = current.get("time")
            times = hourly.get("time", [])
            index = times.index(current_time) if current_time in times else 0
            for field in (
                "shortwave_radiation",
                "direct_radiation",
                "diffuse_radiation",
                "et0_fao_evapotranspiration",
                "soil_moisture_0_to_1cm",
            ):
                values = hourly.get(field, [])
                if isinstance(values, list) and len(values) > index:
                    current[field] = values[index]
        return {"payload": data, "duration_ms": duration_ms, "collected_at": datetime.now(UTC).isoformat()}

    def get_intelligence_air_quality(self, latitude: float, longitude: float) -> dict:
        data, duration_ms = get_json(
            "open_meteo",
            self.AIR_QUALITY_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide,carbon_monoxide",
                "timezone": "UTC",
            },
        )
        return {"payload": data, "duration_ms": duration_ms, "collected_at": datetime.now(UTC).isoformat()}
