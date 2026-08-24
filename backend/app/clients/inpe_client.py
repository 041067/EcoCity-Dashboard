from datetime import datetime

from app.clients.provider_http import ProviderClientError, get_json
from app.core.config import settings


class INPEClient:
    provider = "inpe"

    def get_environmental_alerts(self, latitude: float, longitude: float, radius_km: int = 10) -> dict:
        if not settings.INPE_API_URL:
            raise ProviderClientError(self.provider, "INPE_API_URL is not configured")
        data, duration_ms = get_json(
            self.provider,
            settings.INPE_API_URL,
            params={"latitude": latitude, "longitude": longitude, "radius_km": radius_km},
        )
        return {"payload": data, "duration_ms": duration_ms, "collected_at": datetime.utcnow().isoformat()}
