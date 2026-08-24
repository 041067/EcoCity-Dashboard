from datetime import UTC, datetime, timedelta
from math import cos, radians

from app.clients.provider_http import get_json
from app.core.config import settings


class INPEClient:
    provider = "inpe"
    fire_reference = "https://terrabrasilis.dpi.inpe.br/queimadas/portal/"
    deter_reference = "https://terrabrasilis.dpi.inpe.br/"

    @staticmethod
    def _bbox(latitude: float, longitude: float, radius_km: int) -> tuple[float, float, float, float]:
        latitude_delta = radius_km / 110.574
        longitude_delta = radius_km / max(111.320 * cos(radians(latitude)), 0.001)
        return (
            longitude - longitude_delta,
            latitude - latitude_delta,
            longitude + longitude_delta,
            latitude + latitude_delta,
        )

    @staticmethod
    def _matched_features(data: dict) -> int:
        value = data.get("numberMatched", data.get("totalFeatures"))
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            features = data.get("features", [])
            return len(features) if isinstance(features, list) else 0

    @staticmethod
    def _wfs_params(layer: str, cql_filter: str) -> dict[str, str | int]:
        return {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": layer,
            "outputFormat": "application/json",
            "count": 1,
            "CQL_FILTER": cql_filter,
        }

    def get_environmental_alerts(
        self, latitude: float, longitude: float, radius_km: int | None = None
    ) -> dict:
        radius = radius_km or settings.INPE_ALERT_RADIUS_KM
        now = datetime.now(UTC)
        started_at = now - timedelta(days=settings.INPE_ALERT_LOOKBACK_DAYS)
        min_longitude, min_latitude, max_longitude, max_latitude = self._bbox(latitude, longitude, radius)
        bbox = (
            f"BBOX(geometria,{min_longitude:.6f},{min_latitude:.6f},"
            f"{max_longitude:.6f},{max_latitude:.6f},'EPSG:4326')"
        )
        fire_data, fire_duration = get_json(
            self.provider,
            settings.INPE_FIRE_WFS_URL,
            params=self._wfs_params(
                settings.INPE_FIRE_LAYER,
                f"{bbox} AND data_hora_gmt >= {started_at.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            ),
        )
        deter_bbox = bbox.replace("geometria", "geom")
        deter_data, deter_duration = get_json(
            self.provider,
            settings.INPE_DETER_WFS_URL,
            params=self._wfs_params(
                settings.INPE_DETER_LAYER,
                f"{deter_bbox} AND view_date >= {started_at.date().isoformat()}",
            ),
        )
        return {
            "payload": {
                "fire_alerts": self._matched_features(fire_data),
                "deforestation_alerts": self._matched_features(deter_data),
                "observed_at": now.isoformat(),
                "radius_km": radius,
                "lookback_days": settings.INPE_ALERT_LOOKBACK_DAYS,
                "dataset": "INPE Queimadas + TerraBrasilis DETER Amazonia",
                "source_reference": f"{self.fire_reference} | {self.deter_reference}",
                "scope": "Focos recentes no raio do site; DETER Amazonia cobre a Amazonia Legal.",
            },
            "duration_ms": fire_duration + deter_duration,
            "collected_at": now.isoformat(),
        }
