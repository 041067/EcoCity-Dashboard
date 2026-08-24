from app.clients.provider_http import ProviderClientError
from app.models.esg_topic import ESGTopic
from app.models.materiality_assessment import MaterialityAssessment
from app.models.organization import Organization
from app.models.site import Site
from app.repositories.indicator_repository import IndicatorValueRepository
from app.services.esg_data.climate_risk_service import ClimateRiskService
from app.services.esg_data.normalization_service import NormalizationService
from app.services.esg_data.provider_service import (
    ESGDataProvider,
    ProviderRegistry,
    ProviderService,
)


class FakeNASAPowerProvider(ESGDataProvider):
    name = "nasa_power"
    display_name = "NASA POWER"
    categories = ("climate", "energy")
    ttl_seconds = 86_400
    priority = 3

    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, site):
        self.calls += 1
        return {
            "payload": {
                "properties": {
                    "parameter": {
                        "ALLSKY_SFC_SW_DWN": {"ANN": 5.7},
                        "T2M": {"ANN": 25.1},
                        "PRECTOTCORR": {"ANN": 4.2},
                    }
                }
            }
        }


class OfflineProvider(FakeNASAPowerProvider):
    name = "openaq"
    display_name = "OpenAQ"
    categories = ("air",)
    ttl_seconds = 3_600
    priority = 2

    def fetch(self, site):
        raise ProviderClientError(self.name, "Provider request timed out")


def _organization_site_and_assessment(db_session):
    organization = Organization(name="Eco Industries", organization_type="company", country="Brasil")
    topic = ESGTopic(code="energy", name="Energy", pillar="E", active=True)
    db_session.add_all([organization, topic])
    db_session.flush()
    site = Site(
        organization_id=organization.id,
        name="Factory",
        site_type="factory",
        latitude=-23.55,
        longitude=-46.63,
    )
    assessment = MaterialityAssessment(
        organization_id=organization.id,
        topic_id=topic.id,
        reporting_year=2026,
        status="completed",
    )
    db_session.add_all([site, assessment])
    db_session.commit()
    return organization, site, assessment


def test_normalizes_open_meteo_and_derives_explicit_risks():
    normalized = NormalizationService().normalize(
        "open_meteo",
        {
            "payload": {
                "current": {
                    "time": "2026-08-23T14:00",
                    "temperature_2m": 36.0,
                    "precipitation": 0.0,
                    "wind_speed_10m": 70.0,
                    "et0_fao_evapotranspiration": 5.0,
                }
            }
        },
    )
    risks = ClimateRiskService().derive(normalized)
    levels = {risk.definition.code: risk.metadata["risk_level"] for risk in risks}

    assert {item.definition.code for item in normalized} >= {
        "CLIMATE_TEMPERATURE",
        "CLIMATE_PRECIPITATION",
        "CLIMATE_WIND_SPEED",
    }
    assert levels["CLIMATE_HEAT_RISK"] == "high"
    assert levels["WATER_DROUGHT_RISK"] == "high"
    assert levels["CLIMATE_WIND_RISK"] == "high"


def test_provider_service_caches_values_links_evidence_and_isolates_failures(db_session):
    _, site, assessment = _organization_site_and_assessment(db_session)
    nasa = FakeNASAPowerProvider()
    service = ProviderService(db_session, registry=ProviderRegistry([nasa]))

    first = service.sync_site(site)
    second = service.sync_site(site)

    assert first[0].status == "success"
    assert first[0].values_collected == 3
    assert second[0].status == "cached"
    assert nasa.calls == 1
    assert len(IndicatorValueRepository(db_session).list_for_site(site.id)) == 3
    external = service.evidence.list_for_assessment(assessment.id)
    assert len(external) == 1
    assert external[0].indicator_value.indicator.code == "ENERGY_SOLAR_POTENTIAL"

    outage = ProviderService(db_session, registry=ProviderRegistry([OfflineProvider()])).sync_site(site)
    assert outage[0].status == "failed"


def test_provider_circuit_breaker_uses_cached_fallback_after_repeated_failures(db_session):
    _, site, _ = _organization_site_and_assessment(db_session)
    offline = OfflineProvider()
    offline.name = "offline_test"
    service = ProviderService(db_session, registry=ProviderRegistry([offline]))

    results = [service.sync_site(site)[0].status for _ in range(4)]

    assert results == ["failed", "failed", "failed", "circuit_open"]


def test_esg_intelligence_api_exposes_values_evidence_and_provider_registry(client, db_session):
    organization, site, assessment = _organization_site_and_assessment(db_session)
    ProviderService(db_session, registry=ProviderRegistry([FakeNASAPowerProvider()])).sync_site(site)

    values = client.get(f"/api/v1/esg/sites/{site.id}/energy")
    assert values.status_code == 200
    assert values.json()[0]["indicator"]["category"] == "energy"
    assert values.json()[0]["freshness_status"] == "fresh"
    assert values.json()[0]["source_reference"] == "https://power.larc.nasa.gov/"

    organization_values = client.get(f"/api/v1/esg/organizations/{organization.id}/indicators")
    assert organization_values.status_code == 200
    assert len(organization_values.json()) == 3

    evidence = client.get(f"/api/v1/esg/materiality/{assessment.id}/evidence")
    assert evidence.status_code == 200
    assert evidence.json()[0]["indicator_value"]["indicator"]["code"] == "ENERGY_SOLAR_POTENTIAL"

    providers = client.get("/api/v1/esg/providers")
    assert providers.status_code == 200
    assert {provider["name"] for provider in providers.json()} == {
        "open_meteo", "openaq", "nasa_power", "inpe", "aneel"
    }
