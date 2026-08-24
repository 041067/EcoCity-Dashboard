from datetime import datetime

from app.clients.provider_http import ProviderClientError, get_json
from app.core.config import settings


class OpenAQClient:
    provider = "openaq"

    def get_observations(self, latitude: float, longitude: float) -> dict:
        if not settings.OPENAQ_API_KEY:
            raise ProviderClientError(self.provider, "OPENAQ_API_KEY is not configured")
        headers = {"X-API-Key": settings.OPENAQ_API_KEY}
        locations, location_duration = get_json(
            self.provider,
            f"{settings.OPENAQ_URL.rstrip('/')}/locations",
            params={"coordinates": f"{latitude},{longitude}", "radius": 10000, "limit": 100},
            headers=headers,
        )
        nearest = (locations.get("results") or [None])[0]
        if not isinstance(nearest, dict) or not nearest.get("id"):
            raise ProviderClientError(self.provider, "No OpenAQ location found near this site")
        parameter_by_sensor = {
            sensor.get("id"): (sensor.get("parameter") or {}).get("name")
            for sensor in nearest.get("sensors", [])
            if isinstance(sensor, dict)
        }
        latest, latest_duration = get_json(
            self.provider,
            f"{settings.OPENAQ_URL.rstrip('/')}/locations/{nearest['id']}/latest",
            params={"limit": 100},
            headers=headers,
        )
        measurements = []
        for item in latest.get("results", []):
            if isinstance(item, dict):
                measurements.append({
                    **item,
                    "parameter": parameter_by_sensor.get(item.get("sensorsId")),
                    "location_id": nearest["id"],
                })
        return {
            "payload": {"results": measurements},
            "duration_ms": location_duration + latest_duration,
            "collected_at": datetime.utcnow().isoformat(),
        }
