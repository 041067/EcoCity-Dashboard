import json
from dataclasses import replace

import pytest

from app.clients import (
    aneel_client,
    inpe_client,
    nasa_power_client,
    open_meteo_client,
    openaq_client,
)
from app.clients.aneel_client import ANEELClient
from app.clients.inpe_client import INPEClient
from app.clients.nasa_power_client import NASAPowerClient
from app.clients.open_meteo_client import OpenMeteoClient
from app.clients.openaq_client import OpenAQClient
from app.clients.provider_http import ProviderClientError, get_json, require_https_url
from app.models.city import City
from app.models.esg_topic import ESGTopic
from app.models.materiality_assessment import MaterialityAssessment
from app.models.organization import Organization
from app.models.site import Site
from app.scheduler.collector import Collector
from app.services.esg_data.provider_service import (
    ANEELProvider,
    ESGDataProvider,
    INPEProvider,
    NASAPowerProvider,
    OpenAQProvider,
    OpenMeteoProvider,
    ProviderRegistry,
    ProviderService,
)


def test_open_meteo_client_collects_climate_and_air_payloads(monkeypatch):
    calls = []

    def fake_get_json(provider, url, *, params=None, headers=None):
        calls.append((provider, url, params))
        if "air-quality" in url:
            return {"current": {"time": "2026-08-24T12:00", "pm2_5": 8.2}}, 9
        return {"current": {"time": "2026-08-24T12:00", "temperature_2m": 28.0}, "hourly": {}}, 7

    monkeypatch.setattr(open_meteo_client, "get_json", fake_get_json)

    climate = OpenMeteoClient().get_intelligence_climate(-23.55, -46.63)
    air = OpenMeteoClient().get_intelligence_air_quality(-23.55, -46.63)

    assert climate["payload"]["current"]["temperature_2m"] == 28.0
    assert air["payload"]["current"]["pm2_5"] == 8.2
    assert [call[0] for call in calls] == ["open_meteo", "open_meteo"]


def test_openaq_client_uses_nearest_location_and_sensor_parameter(monkeypatch):
    monkeypatch.setattr(openaq_client.settings, "OPENAQ_API_KEY", "test-key")

    def fake_get_json(provider, url, *, params=None, headers=None):
        assert provider == "openaq"
        assert headers == {"X-API-Key": "test-key"}
        if url.endswith("/locations"):
            return {
                "results": [{"id": 99, "sensors": [{"id": 4, "parameter": {"name": "pm25"}}]}]
            }, 12
        assert url.endswith("/locations/99/latest")
        return {
            "results": [
                {"sensorsId": 4, "value": 11.5, "datetime": {"utc": "2026-08-24T12:00:00Z"}}
            ]
        }, 8

    monkeypatch.setattr(openaq_client, "get_json", fake_get_json)

    payload = OpenAQClient().get_observations(-23.55, -46.63)

    assert payload["duration_ms"] == 20
    assert payload["payload"]["results"] == [
        {
            "sensorsId": 4,
            "value": 11.5,
            "datetime": {"utc": "2026-08-24T12:00:00Z"},
            "parameter": "pm25",
            "location_id": 99,
        }
    ]


def test_nasa_power_client_uses_climatology_contract(monkeypatch):
    def fake_get_json(provider, url, *, params=None, headers=None):
        assert provider == "nasa_power"
        assert url.endswith("/temporal/climatology/point")
        assert params["parameters"] == "ALLSKY_SFC_SW_DWN,T2M,PRECTOTCORR"
        return {"properties": {"parameter": {}}}, 18

    monkeypatch.setattr(nasa_power_client, "get_json", fake_get_json)

    payload = NASAPowerClient().get_climatology(-23.55, -46.63)

    assert payload["payload"] == {"properties": {"parameter": {}}}
    assert payload["duration_ms"] == 18


def test_inpe_client_queries_recent_fire_and_deter_alerts(monkeypatch):
    calls = []

    def fake_get_json(provider, url, *, params=None, headers=None):
        calls.append((url, params))
        if url == inpe_client.settings.INPE_FIRE_WFS_URL:
            assert params["typeNames"] == inpe_client.settings.INPE_FIRE_LAYER
            assert "BBOX(geometria," in params["CQL_FILTER"]
            assert "data_hora_gmt >=" in params["CQL_FILTER"]
            return {"numberMatched": 7}, 13
        assert url == inpe_client.settings.INPE_DETER_WFS_URL
        assert params["typeNames"] == inpe_client.settings.INPE_DETER_LAYER
        assert "BBOX(geom," in params["CQL_FILTER"]
        assert "view_date >=" in params["CQL_FILTER"]
        return {"totalFeatures": 2}, 17

    monkeypatch.setattr(inpe_client, "get_json", fake_get_json)

    payload = INPEClient().get_environmental_alerts(-23.55, -46.63, radius_km=12)

    assert payload["payload"]["fire_alerts"] == 7
    assert payload["payload"]["deforestation_alerts"] == 2
    assert payload["payload"]["radius_km"] == 12
    assert payload["duration_ms"] == 30
    assert len(calls) == 2


def test_aneel_client_aggregates_state_capacity_and_renewable_share(monkeypatch):
    def fake_get_json(provider, url, *, params=None, headers=None):
        assert provider == "aneel"
        assert url == aneel_client.settings.ANEEL_DATASTORE_URL
        assert json.loads(params["filters"]) == {"DscFaseUsina": "Operação", "SigUFPrincipal": "SP"}
        return {
            "result": {
                "total": 3,
                "records": [
                    {
                        "MdaPotenciaFiscalizadaKw": "1.500,00",
                        "DscOrigemCombustivel": "Hídrica",
                        "DatGeracaoConjuntoDados": "2026-08-20",
                    },
                    {
                        "MdaPotenciaFiscalizadaKw": "500",
                        "DscOrigemCombustivel": "Solar",
                        "DatGeracaoConjuntoDados": "2026-08-20",
                    },
                    {
                        "MdaPotenciaFiscalizadaKw": "1000",
                        "DscOrigemCombustivel": "Fóssil",
                        "DatGeracaoConjuntoDados": "2026-08-20",
                    },
                ],
            }
        }, 21

    monkeypatch.setattr(aneel_client, "get_json", fake_get_json)

    payload = ANEELClient().get_energy_context("sp")

    assert payload["payload"]["installed_capacity_mw"] == 3.0
    assert payload["payload"]["renewable_share"] == pytest.approx(66.67)
    assert payload["payload"]["state"] == "SP"
    assert payload["duration_ms"] == 21


def test_provider_http_rejects_non_https_urls_and_retries_transient_error(monkeypatch):
    assert require_https_url("https://example.test/data", "test") == "https://example.test/data"
    with pytest.raises(ProviderClientError, match="HTTPS"):
        require_https_url("http://example.test/data", "test")

    responses = [
        type("Response", (), {"status_code": 503})(),
        type(
            "Response",
            (),
            {
                "status_code": 200,
                "raise_for_status": lambda self: None,
                "json": lambda self: {"ok": True},
            },
        )(),
    ]

    def fake_get(*args, **kwargs):
        response = responses.pop(0)
        if response.status_code == 503:
            response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr("app.clients.provider_http.httpx.get", fake_get)

    payload, _ = get_json("test", "https://example.test/data")
    assert payload == {"ok": True}
    assert not responses


class FakeOpenMeteoClient:
    def get_intelligence_climate(self, latitude, longitude):
        return {
            "payload": {
                "current": {
                    "time": "2026-08-24T12:00:00Z",
                    "temperature_2m": 31.0,
                    "precipitation": 0.0,
                    "wind_speed_10m": 12.0,
                }
            }
        }

    def get_intelligence_air_quality(self, latitude, longitude):
        return {"payload": {"current": {"time": "2026-08-24T12:00:00Z", "pm2_5": 9.0}}}


class FakeOpenAQClient:
    def get_observations(self, latitude, longitude):
        return {
            "payload": {
                "results": [
                    {"parameter": "no2", "value": 11.0, "datetime": {"utc": "2026-08-24T12:00:00Z"}}
                ]
            }
        }


class FakeNASAPowerClient:
    def get_climatology(self, latitude, longitude):
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


class FakeINPEClient:
    def get_environmental_alerts(self, latitude, longitude):
        return {
            "payload": {
                "fire_alerts": 2,
                "deforestation_alerts": 1,
                "observed_at": "2026-08-24T12:00:00Z",
                "source_reference": "https://terrabrasilis.dpi.inpe.br/",
            }
        }


class FakeANEELClient:
    def get_energy_context(self, state_code):
        assert state_code == "SP"
        return {
            "payload": {
                "renewable_share": 84.0,
                "installed_capacity_mw": 2400.0,
                "observed_at": "2026-08-20",
                "source_reference": "https://dadosabertos.aneel.gov.br/",
            }
        }


def test_all_five_providers_reach_indicator_values_and_materiality_evidence(
    db_session, monkeypatch
):
    monkeypatch.setattr(
        "app.services.esg_data.provider_service.settings.OPENAQ_API_KEY", "test-key"
    )
    organization = Organization(
        name="Eco Industries", organization_type="company", country="Brasil"
    )
    city = City(name="São Paulo", state="SP", latitude=-23.55, longitude=-46.63)
    db_session.add_all([organization, city])
    db_session.flush()
    site = Site(
        organization_id=organization.id,
        city_id=city.id,
        name="Fábrica São Paulo",
        site_type="factory",
        latitude=-23.55,
        longitude=-46.63,
    )
    topic_codes = [
        "energy",
        "air-quality",
        "biodiversity",
        "ghg-emissions",
        "risk-management",
        "water",
    ]
    topics = [ESGTopic(code=code, name=code, pillar="E", active=True) for code in topic_codes]
    db_session.add_all([site, *topics])
    db_session.flush()
    db_session.add_all(
        [
            MaterialityAssessment(
                organization_id=organization.id,
                topic_id=topic.id,
                reporting_year=2026,
                status="completed",
            )
            for topic in topics
        ]
    )
    db_session.commit()

    registry = ProviderRegistry(
        [
            OpenMeteoProvider(FakeOpenMeteoClient()),
            OpenAQProvider(FakeOpenAQClient()),
            NASAPowerProvider(FakeNASAPowerClient()),
            INPEProvider(FakeINPEClient()),
            ANEELProvider(FakeANEELClient()),
        ]
    )
    service = ProviderService(db_session, registry=registry)
    results = service.sync_site(site)

    assert {result.provider for result in results if result.status == "success"} == {
        "open_meteo",
        "openaq",
        "nasa_power",
        "inpe",
        "aneel",
    }
    values_by_source = {value.source for value in service.values.list_for_site(site.id, limit=100)}
    assert values_by_source >= {"open_meteo", "openaq", "nasa_power", "inpe", "aneel"}
    linked_sources = {
        evidence.indicator_value.source
        for topic in topics
        for evidence in service.evidence.list_for_assessment(
            db_session.query(MaterialityAssessment)
            .filter(MaterialityAssessment.topic_id == topic.id)
            .one()
            .id
        )
    }
    assert linked_sources >= {"open_meteo", "openaq", "nasa_power", "inpe", "aneel"}


def test_scheduler_registers_all_sprint_8_jobs():
    collector = Collector()
    collector.start()
    try:
        assert {job.id for job in collector.scheduler.get_jobs()} >= {
            "esg_open_meteo_15min",
            "esg_openaq_hourly",
            "esg_nasa_daily",
            "esg_inpe_daily",
            "esg_aneel_daily",
        }
    finally:
        collector.shutdown()


class CachedThenFailingProvider(ESGDataProvider):
    name = "cache_fallback_test"
    display_name = "Cache fallback test"
    categories = ("climate", "energy")
    ttl_seconds = 0
    priority = 3

    def __init__(self):
        self.failing = False

    def fetch(self, site):
        if self.failing:
            raise ProviderClientError(self.name, "temporary outage")
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

    def normalize(self, payload, normalizer):
        return [
            replace(item, source=self.name) for item in normalizer.normalize("nasa_power", payload)
        ]


def test_circuit_breaker_reports_cached_fallback_when_values_exist(db_session):
    organization = Organization(
        name="Eco Industries", organization_type="company", country="Brasil"
    )
    db_session.add(organization)
    db_session.flush()
    site = Site(
        organization_id=organization.id,
        name="Factory",
        site_type="factory",
        latitude=-23.55,
        longitude=-46.63,
    )
    db_session.add(site)
    db_session.commit()

    provider = CachedThenFailingProvider()
    service = ProviderService(db_session, registry=ProviderRegistry([provider]))
    assert service.sync_site(site)[0].status == "success"

    provider.failing = True
    results = [service.sync_site(site)[0] for _ in range(4)]

    assert [result.status for result in results] == ["failed", "failed", "failed", "circuit_open"]
    assert results[-1].cached is True
    assert results[-1].message == "Circuit open; cached values remain available"
