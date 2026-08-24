from datetime import datetime

from app.clients.provider_http import get_json
from app.core.config import settings


class NASAPowerClient:
    provider = "nasa_power"

    def get_climatology(self, latitude: float, longitude: float) -> dict:
        data, duration_ms = get_json(
            self.provider,
            f"{settings.NASA_POWER_URL.rstrip('/')}/temporal/climatology/point",
            params={
                "parameters": "ALLSKY_SFC_SW_DWN,T2M,PRECTOTCORR",
                "community": "RE",
                "longitude": longitude,
                "latitude": latitude,
                "format": "JSON",
            },
        )
        return {"payload": data, "duration_ms": duration_ms, "collected_at": datetime.utcnow().isoformat()}
