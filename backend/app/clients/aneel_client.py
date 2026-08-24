from datetime import datetime

from app.clients.provider_http import ProviderClientError, get_json
from app.core.config import settings


class ANEELClient:
    provider = "aneel"

    def get_energy_context(self, latitude: float, longitude: float) -> dict:
        if not settings.ANEEL_API_URL:
            raise ProviderClientError(self.provider, "ANEEL_API_URL is not configured")
        data, duration_ms = get_json(
            self.provider,
            settings.ANEEL_API_URL,
            params={"latitude": latitude, "longitude": longitude},
        )
        return {"payload": data, "duration_ms": duration_ms, "collected_at": datetime.utcnow().isoformat()}
