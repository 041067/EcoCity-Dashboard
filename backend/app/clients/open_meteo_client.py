import httpx

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
