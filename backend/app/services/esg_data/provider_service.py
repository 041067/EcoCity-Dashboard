from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from time import monotonic
from typing import Any

from sqlalchemy.orm import Session

from app.clients.aneel_client import ANEELClient
from app.clients.inpe_client import INPEClient
from app.clients.nasa_power_client import NASAPowerClient
from app.clients.open_meteo_client import OpenMeteoClient
from app.clients.openaq_client import OpenAQClient
from app.clients.provider_http import ProviderClientError
from app.core.config import settings
from app.logs.logger import logger
from app.models.site import Site
from app.repositories.indicator_repository import IndicatorRepository, IndicatorValueRepository
from app.repositories.provider_sync_repository import ProviderSyncRepository
from app.services.esg_data.climate_risk_service import ClimateRiskService
from app.services.esg_data.evidence_service import EvidenceService
from app.services.esg_data.normalization_service import NormalizationService, NormalizedIndicator


class ESGDataProvider(ABC):
    """Stable contract that isolates the rest of EcoCity from provider-specific APIs."""

    name: str
    display_name: str
    categories: tuple[str, ...]
    ttl_seconds: int
    priority: int

    @abstractmethod
    def fetch(self, site: Site) -> dict[str, Any]: ...

    def normalize(self, payload: dict[str, Any], normalizer: NormalizationService) -> list[NormalizedIndicator]:
        return normalizer.normalize(self.name, payload)

    def health_check(self) -> dict[str, str]:
        return {"status": "not_checked"}

    def configuration_error(self) -> str | None:
        return None


class OpenMeteoProvider(ESGDataProvider):
    name, display_name = "open_meteo", "Open-Meteo"
    categories, ttl_seconds, priority = ("climate", "air", "energy", "water"), 15 * 60, 1

    def __init__(self, client: OpenMeteoClient | None = None) -> None:
        self.client = client or OpenMeteoClient()

    def fetch(self, site: Site) -> dict[str, Any]:
        climate = self.client.get_intelligence_climate(site.latitude, site.longitude)
        air = self.client.get_intelligence_air_quality(site.latitude, site.longitude)
        return {"climate": climate, "air": air}

    def normalize(self, payload: dict[str, Any], normalizer: NormalizationService) -> list[NormalizedIndicator]:
        climate = {**payload["climate"], "channel": "climate"}
        air = {**payload["air"], "channel": "air"}
        return normalizer.normalize(self.name, climate) + normalizer.normalize(self.name, air)


class OpenAQProvider(ESGDataProvider):
    name, display_name = "openaq", "OpenAQ"
    categories, ttl_seconds, priority = ("air",), 60 * 60, 2

    def __init__(self, client: OpenAQClient | None = None) -> None:
        self.client = client or OpenAQClient()

    def fetch(self, site: Site) -> dict[str, Any]:
        return self.client.get_observations(site.latitude, site.longitude)

    def configuration_error(self) -> str | None:
        if not settings.OPENAQ_API_KEY:
            return "OPENAQ_API_KEY is not configured"
        return None


class NASAPowerProvider(ESGDataProvider):
    name, display_name = "nasa_power", "NASA POWER"
    categories, ttl_seconds, priority = ("climate", "energy"), 24 * 60 * 60, 3

    def __init__(self, client: NASAPowerClient | None = None) -> None:
        self.client = client or NASAPowerClient()

    def fetch(self, site: Site) -> dict[str, Any]:
        return self.client.get_climatology(site.latitude, site.longitude)


class INPEProvider(ESGDataProvider):
    name, display_name = "inpe", "INPE"
    categories, ttl_seconds, priority = ("territory",), 24 * 60 * 60, 4

    def __init__(self, client: INPEClient | None = None) -> None:
        self.client = client or INPEClient()

    def fetch(self, site: Site) -> dict[str, Any]:
        return self.client.get_environmental_alerts(site.latitude, site.longitude)


class ANEELProvider(ESGDataProvider):
    name, display_name = "aneel", "ANEEL"
    categories, ttl_seconds, priority = ("energy",), 24 * 60 * 60, 5

    def __init__(self, client: ANEELClient | None = None) -> None:
        self.client = client or ANEELClient()

    def fetch(self, site: Site) -> dict[str, Any]:
        state_code = site.city.state if site.city else None
        return self.client.get_energy_context(state_code)


class ProviderRegistry:
    def __init__(self, providers: list[ESGDataProvider] | None = None) -> None:
        self._providers = {provider.name: provider for provider in (providers or [
            OpenMeteoProvider(), OpenAQProvider(), NASAPowerProvider(), INPEProvider(), ANEELProvider(),
        ])}

    def get(self, name: str) -> ESGDataProvider | None:
        return self._providers.get(name)

    def all(self) -> list[ESGDataProvider]:
        return sorted(self._providers.values(), key=lambda provider: provider.priority)


@dataclass
class ProviderSyncResult:
    provider: str
    status: str
    cached: bool
    values_collected: int
    duration_ms: int | None = None
    message: str | None = None


class ProviderService:
    """Fetches safely, uses the indicator store as cache and never lets a provider failure escape."""

    FAILURE_THRESHOLD = 3
    CIRCUIT_SECONDS = 5 * 60
    _failures: dict[str, int] = {}
    _open_until: dict[str, datetime] = {}

    def __init__(
        self,
        db: Session,
        registry: ProviderRegistry | None = None,
        normalizer: NormalizationService | None = None,
    ) -> None:
        self.db = db
        self.registry = registry or ProviderRegistry()
        self.normalizer = normalizer or NormalizationService()
        self.indicators = IndicatorRepository(db)
        self.values = IndicatorValueRepository(db)
        self.logs = ProviderSyncRepository(db)
        self.evidence = EvidenceService(db)
        self.risks = ClimateRiskService()

    def sync_site(self, site: Site, provider_names: list[str] | None = None) -> list[ProviderSyncResult]:
        requested = provider_names or [provider.name for provider in self.registry.all()]
        results: list[ProviderSyncResult] = []
        for name in requested:
            provider = self.registry.get(name)
            if provider is None:
                results.append(ProviderSyncResult(name, "unsupported", False, 0, message="Unknown provider"))
                continue
            results.append(self._sync_provider(site, provider))
        return results

    def _sync_provider(self, site: Site, provider: ESGDataProvider) -> ProviderSyncResult:
        if site.latitude is None or site.longitude is None:
            return self._result(provider, site, "skipped", 0, message="Site has no latitude/longitude")
        if configuration_error := provider.configuration_error():
            return self._result(provider, site, "not_configured", 0, message=configuration_error)
        now = datetime.now(UTC)
        if self._open_until.get(provider.name, now) > now:
            cached = self.values.has_provider_data(site.id, provider.name)
            message = "Circuit open; cached values remain available" if cached else "Circuit open; no cached values available"
            return self._result(provider, site, "circuit_open", 0, message=message, cached=cached)
        if self.values.has_fresh_provider_data(site.id, provider.name, provider.ttl_seconds):
            return self._result(provider, site, "cached", 0, cached=True, message="Recent cached values available")
        started = monotonic()
        try:
            raw = provider.fetch(site)
            normalized = provider.normalize(raw, self.normalizer)
            if provider.name == "open_meteo":
                normalized.extend(self.risks.derive(normalized))
            if not normalized:
                raise ProviderClientError(provider.name, "Provider returned no supported indicators")
            saved = self._persist(site, normalized)
            self.db.commit()
            self._failures.pop(provider.name, None)
            return self._result(provider, site, "success", len(saved), int((monotonic() - started) * 1000))
        except (ProviderClientError, KeyError, TypeError, ValueError) as exc:
            self.db.rollback()
            self._record_failure(provider.name)
            logger.warning(
                "provider=%s operation=sync status=failed site_id=%s message=%s",
                provider.name,
                site.id,
                str(exc),
            )
            return self._result(provider, site, "failed", 0, int((monotonic() - started) * 1000), str(exc))
        except Exception:
            self.db.rollback()
            self._record_failure(provider.name)
            logger.exception("provider=%s operation=sync status=failed site_id=%s", provider.name, site.id)
            return self._result(provider, site, "failed", 0, int((monotonic() - started) * 1000), "Provider sync failed")

    def _persist(self, site: Site, normalized: list[NormalizedIndicator]):
        saved = []
        for item in normalized:
            definition = self.indicators.get_or_create(
                code=item.definition.code,
                name=item.definition.name,
                pillar=item.definition.pillar,
                category=item.definition.category,
                unit=item.definition.unit,
                description=item.definition.description,
                source_type=item.definition.source_type,
            )
            confidence = round((item.quality_score * 0.7) + (item.relevance_score * 0.3), 2)
            value = self.values.create(
                indicator_id=definition.id,
                organization_id=site.organization_id,
                site_id=site.id,
                value=item.value,
                unit=item.definition.unit,
                source=item.source,
                source_reference=item.source_reference,
                latitude=site.latitude,
                longitude=site.longitude,
                observed_at=item.observed_at,
                source_metadata=item.metadata,
                quality_score=item.quality_score,
                freshness_score=100.0,
                relevance_score=item.relevance_score,
                confidence_score=confidence,
            )
            self.evidence.link_value(value)
            saved.append(value)
        return saved

    def _record_failure(self, provider: str) -> None:
        failures = self._failures.get(provider, 0) + 1
        self._failures[provider] = failures
        if failures >= self.FAILURE_THRESHOLD:
            self._open_until[provider] = datetime.now(UTC).replace(microsecond=0) + timedelta(seconds=self.CIRCUIT_SECONDS)

    def _result(
        self,
        provider: ESGDataProvider,
        site: Site,
        status: str,
        values_collected: int,
        duration_ms: int | None = None,
        message: str | None = None,
        cached: bool = False,
    ) -> ProviderSyncResult:
        self.logs.log(
            provider=provider.name,
            site_id=site.id,
            status=status,
            data_category=",".join(provider.categories),
            duration_ms=duration_ms,
            message=message,
        )
        self.db.commit()
        logger.info(
            "provider=%s operation=sync status=%s duration_ms=%s site_id=%s values=%s",
            provider.name,
            status,
            duration_ms,
            site.id,
            values_collected,
        )
        return ProviderSyncResult(provider.name, status, cached, values_collected, duration_ms, message)

    def provider_statuses(self) -> list[dict[str, Any]]:
        latest = self.logs.latest_by_provider()
        result = []
        for provider in self.registry.all():
            log = latest.get(provider.name)
            status = "unknown"
            message = log.message if log else None
            if configuration_error := provider.configuration_error():
                status = "offline"
                message = configuration_error
            elif log:
                status = "online" if log.status in {"success", "cached"} else "degraded"
                if log.status in {"failed", "circuit_open"}:
                    status = "offline"
            result.append({
                "name": provider.name,
                "display_name": provider.display_name,
                "status": status,
                "last_sync": log.created_at if log else None,
                "data_categories": list(provider.categories),
                "priority": provider.priority,
                "last_message": message,
            })
        return result
