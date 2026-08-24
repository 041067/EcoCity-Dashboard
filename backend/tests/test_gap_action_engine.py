from app.models.esg_indicator import ESGIndicator
from app.models.esg_topic import ESGTopic
from app.models.indicator_value import IndicatorValue
from app.models.organization_esg_topic import OrganizationESGTopic
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.site_repository import SiteRepository
from app.services.gap_action_service import GapService, OpportunityService, RiskService


def _organization_with_esg_evidence(db_session):
    organization = OrganizationRepository(db_session).create(
        name="Sprint 9 Organization", organization_type="company", country="Brasil"
    )
    site = SiteRepository(db_session).create(
        organization.id, name="Factory", site_type="factory", latitude=-23.5, longitude=-46.6
    )
    air = ESGTopic(code="air-quality", name="Air quality", pillar="E", active=True)
    risk = ESGTopic(code="risk-management", name="Risk management", pillar="G", active=True)
    energy = ESGTopic(code="energy", name="Energy", pillar="E", active=True)
    air_indicator = ESGIndicator(
        code="AIR_PM25", name="PM2.5", pillar="E", category="air", unit="ug/m3",
        source_type="external", direction="lower_is_better", active=True,
    )
    risk_indicator = ESGIndicator(
        code="CLIMATE_HEAT_RISK", name="Heat risk", pillar="E", category="risk", unit="index",
        source_type="derived", direction="lower_is_better", active=True,
    )
    solar_indicator = ESGIndicator(
        code="ENERGY_SOLAR_POTENTIAL", name="Solar potential", pillar="E", category="energy",
        unit="kWh/m2/day", source_type="external", direction="higher_is_better", active=True,
    )
    db_session.add_all([air, risk, energy, air_indicator, risk_indicator, solar_indicator])
    db_session.flush()
    db_session.add_all(
        [
            OrganizationESGTopic(organization_id=organization.id, topic_id=air.id, enabled=True, priority=3),
            OrganizationESGTopic(organization_id=organization.id, topic_id=risk.id, enabled=True, priority=3),
            OrganizationESGTopic(organization_id=organization.id, topic_id=energy.id, enabled=True, priority=3),
            IndicatorValue(
                indicator_id=air_indicator.id, organization_id=organization.id, site_id=site.id,
                value=30, unit="ug/m3", source="openaq", confidence_score=90,
            ),
            IndicatorValue(
                indicator_id=risk_indicator.id, organization_id=organization.id, site_id=site.id,
                value=4, unit="index", source="climate_risk_engine", confidence_score=100,
            ),
            IndicatorValue(
                indicator_id=solar_indicator.id, organization_id=organization.id, site_id=site.id,
                value=5.7, unit="kWh/m2/day", source="nasa_power", confidence_score=90,
            ),
        ]
    )
    db_session.commit()
    return organization, site, air, risk, energy, air_indicator


def test_deterministic_gap_risk_opportunity_boundaries():
    assert GapService.gap_value(30, 10, "lower_is_better") == 20
    assert GapService.gap_value(30, 50, "higher_is_better") == 20
    assert GapService.severity(10, 10, "lower_is_better") is None
    assert GapService.severity(10.5, 10, "lower_is_better") == "low"
    assert GapService.severity(13, 10, "lower_is_better") == "high"
    assert GapService.tracking(100, 2024, 50, 2030, 50, "lower_is_better", 2026) == (100.0, "achieved")
    assert RiskService.calculate(5, 5) == (100.0, "critical")
    assert OpportunityService.calculate(4, 4) == (64.0, "high")


def test_analysis_is_idempotent_and_reaches_priority_evidence(client, db_session):
    organization, site, air, _, _, air_indicator = _organization_with_esg_evidence(db_session)
    target_response = client.post(
        f"/api/v1/esg/organizations/{organization.id}/targets",
        json={
            "topic_id": air.id,
            "indicator_id": air_indicator.id,
            "site_id": site.id,
            "name": "Reduce PM2.5",
            "baseline_value": 20,
            "baseline_year": 2025,
            "target_value": 10,
            "target_year": 2030,
        },
    )
    assert target_response.status_code == 201
    assert target_response.json()["direction"] == "lower_is_better"
    assert target_response.json()["tracking_status"] == "at_risk"

    first = client.post(f"/api/v1/esg/organizations/{organization.id}/analysis/run")
    assert first.status_code == 200
    assert first.json()["created"] == {"gaps": 1, "risks": 1, "opportunities": 1}
    second = client.post(f"/api/v1/esg/organizations/{organization.id}/analysis/run")
    assert second.status_code == 200
    assert second.json()["created"] == {"gaps": 0, "risks": 0, "opportunities": 0}
    assert second.json()["updated"] == {"gaps": 1, "risks": 1, "opportunities": 1}

    gaps = client.get(f"/api/v1/esg/organizations/{organization.id}/gaps")
    assert gaps.status_code == 200
    assert gaps.json()[0]["severity"] == "critical"
    assert gaps.json()[0]["source"] == "openaq"
    assert client.get(f"/api/v1/esg/organizations/{organization.id}/risks/matrix").status_code == 200
    assert client.get(f"/api/v1/esg/organizations/{organization.id}/opportunities").json()[0]["opportunity_type"] == "solar_generation"
    priorities = client.get(f"/api/v1/esg/organizations/{organization.id}/priorities")
    assert priorities.status_code == 200
    assert priorities.json()[0]["explanation"].startswith("score = materiality")
    assert client.get(f"/api/v1/esg/organizations/{organization.id}/audit").json()[0]["entity_type"] == "analysis_run"


def test_actions_are_scoped_audited_and_progress_is_task_derived(client, db_session):
    organization, site, air, _, _, air_indicator = _organization_with_esg_evidence(db_session)
    target = client.post(
        f"/api/v1/esg/organizations/{organization.id}/targets",
        json={
            "topic_id": air.id, "indicator_id": air_indicator.id, "site_id": site.id,
            "name": "Reduce PM2.5", "baseline_value": 20, "baseline_year": 2025,
            "target_value": 10, "target_year": 2030,
        },
    ).json()
    client.post(f"/api/v1/esg/organizations/{organization.id}/analysis/run")
    gap = client.get(f"/api/v1/esg/organizations/{organization.id}/gaps").json()[0]
    rejected = client.post(
        f"/api/v1/esg/organizations/{organization.id}/actions",
        json={"topic_id": air.id, "title": "Bad assignment", "priority": "critical"},
    )
    assert rejected.status_code == 422
    action = client.post(
        f"/api/v1/esg/organizations/{organization.id}/actions",
        json={"topic_id": air.id, "site_id": site.id, "gap_id": gap["id"], "title": "Filter review"},
    )
    assert action.status_code == 201
    task = client.post(
        f"/api/v1/esg/organizations/{organization.id}/actions/{action.json()['id']}/tasks",
        json={"title": "Inspect filters"},
    )
    assert task.status_code == 201
    completed = client.put(
        f"/api/v1/esg/organizations/{organization.id}/actions/{action.json()['id']}/tasks/{task.json()['id']}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    action_after = client.get(f"/api/v1/esg/organizations/{organization.id}/actions/{action.json()['id']}")
    assert action_after.json()["progress_percentage"] == 100
    assert action_after.json()["status"] == "completed"

    other = OrganizationRepository(db_session).create(
        name="Other org", organization_type="company", country="Brasil"
    )
    assert client.put(
        f"/api/v1/esg/organizations/{other.id}/targets/{target['id']}", json={"name": "cross org"}
    ).status_code == 404
    assert client.get(f"/api/v1/esg/organizations/{other.id}/gaps").json() == []
