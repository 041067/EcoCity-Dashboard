from app.clients.open_meteo_client import OpenMeteoClient
from app.logs.logger import logger
from app.repositories.city_repository import CityRepository
from app.repositories.reading_repository import ReadingRepository

MONITORED_CITIES = [
    {"name": "São Paulo", "state": "SP", "latitude": -23.5505, "longitude": -46.6333},
    {"name": "Rio de Janeiro", "state": "RJ", "latitude": -22.9068, "longitude": -43.1729},
    {"name": "Curitiba", "state": "PR", "latitude": -25.4290, "longitude": -49.2671},
    {"name": "Manaus", "state": "AM", "latitude": -3.1190, "longitude": -60.0217},
    {"name": "Recife", "state": "PE", "latitude": -8.0476, "longitude": -34.8770},
]


class WeatherService:
    def __init__(self, city_repo: CityRepository, reading_repo: ReadingRepository) -> None:
        self.client = OpenMeteoClient()
        self.city_repo = city_repo
        self.reading_repo = reading_repo

    def collect_all(self) -> list[dict]:
        results = []
        for city_info in MONITORED_CITIES:
            result = self._collect_one(city_info)
            results.append(result)
        return results

    def collect_one(self, city_name: str) -> dict | None:
        city_info = next((c for c in MONITORED_CITIES if c["name"].lower() == city_name.lower()), None)
        if not city_info:
            logger.warning("City %s not in monitored list", city_name)
            return None
        return self._collect_one(city_info)

    def _collect_one(self, city_info: dict) -> dict:
        city = self.city_repo.get_or_create(
            name=city_info["name"],
            state=city_info["state"],
            latitude=city_info["latitude"],
            longitude=city_info["longitude"],
        )

        weather = self.client.get_weather(city.latitude, city.longitude)
        air = self.client.get_air_quality(city.latitude, city.longitude)

        reading = self.reading_repo.create(
            city_id=city.id,
            temperature=weather.get("temperature_2m", 0.0),
            humidity=weather.get("relative_humidity_2m", 0.0),
            pm25=air.get("pm2_5", 0.0),
            pm10=air.get("pm10", 0.0),
            ozone=air.get("ozone", 0.0),
            carbon_monoxide=air.get("carbon_monoxide", 0.0),
            wind_speed=weather.get("wind_speed_10m", 0.0),
        )

        logger.info("Data collected for %s (reading_id=%s)", city.name, reading.id)
        return {
            "city": city.name,
            "state": city.state,
            "reading_id": reading.id,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "pm25": reading.pm25,
            "pm10": reading.pm10,
            "ozone": reading.ozone,
            "carbon_monoxide": reading.carbon_monoxide,
            "wind_speed": reading.wind_speed,
            "created_at": reading.created_at.isoformat() if reading.created_at else None,
        }
