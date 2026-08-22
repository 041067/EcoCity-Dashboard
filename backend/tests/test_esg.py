from app.models.city import City
from app.models.esg_topic import ESGTopic
from app.repositories.esg_topic_repository import ESGTopicRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.stakeholder_repository import StakeholderRepository


def _create_topic(db_session, code: str = "energy", pillar: str = "E") -> ESGTopic:
    topic = ESGTopic(code=code, name="Energy", pillar=pillar, description="Energy management")
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)
    return topic


def test_esg_repositories_create_and_query_domain(db_session):
    organization = OrganizationRepository(db_session).create(
        name="Eco Industries",
        organization_type="company",
        country="Brasil",
    )
    city = City(name="São Paulo", state="SP", latitude=-23.55, longitude=-46.63)
    db_session.add(city)
    db_session.commit()
    db_session.refresh(city)

    SiteRepository(db_session).create(
        organization.id,
        name="Fábrica São Paulo",
        site_type="factory",
        city_id=city.id,
    )
    stakeholder = StakeholderRepository(db_session).create(
        organization.id,
        name="Comunidade",
        stakeholder_type="community",
        influence_level=3,
        impact_level=5,
    )
    topic = _create_topic(db_session)
    link = ESGTopicRepository(db_session).create_or_update_link(
        organization.id, topic.id, enabled=True, priority=5, notes="Material para a operação"
    )

    assert SiteRepository(db_session).list_by_organization(organization.id)[0].city.name == "São Paulo"
    assert StakeholderRepository(db_session).list_by_organization(organization.id) == [stakeholder]
    assert link.topic.code == "energy"
    assert ESGTopicRepository(db_session).list_by_organization(organization.id)[0].priority == 5


def test_esg_api_onboarding_flow_and_overview(client, db_session):
    city = City(name="Curitiba", state="PR", latitude=-25.42, longitude=-49.27)
    db_session.add(city)
    db_session.commit()
    db_session.refresh(city)
    topic_e = _create_topic(db_session, "water", "E")
    topic_s = _create_topic(db_session, "community-relations", "S")
    topic_g = _create_topic(db_session, "compliance", "G")

    create_organization = client.post(
        "/api/v1/esg/organizations",
        json={
            "name": "Eco Industries S.A.",
            "organization_type": "company",
            "industry_sector": "Indústria",
            "country": "Brasil",
        },
    )
    assert create_organization.status_code == 201
    organization_id = create_organization.json()["id"]

    assert client.put(
        f"/api/v1/esg/organizations/{organization_id}/profile",
        json={
            "reporting_year": 2026,
            "environmental_enabled": True,
            "social_enabled": True,
            "governance_enabled": True,
            "esg_maturity_level": "developing",
        },
    ).status_code == 200
    site = client.post(
        f"/api/v1/esg/organizations/{organization_id}/sites",
        json={"name": "Centro Curitiba", "site_type": "office", "city_id": city.id},
    )
    assert site.status_code == 201
    assert site.json()["city"]["name"] == "Curitiba"
    stakeholder = client.post(
        f"/api/v1/esg/organizations/{organization_id}/stakeholders",
        json={
            "name": "Comunidade local",
            "stakeholder_type": "community",
            "influence_level": 3,
            "impact_level": 5,
        },
    )
    assert stakeholder.status_code == 201

    for topic in (topic_e, topic_s, topic_g):
        response = client.post(
            f"/api/v1/esg/organizations/{organization_id}/topics",
            json={"topic_id": topic.id, "priority": 4},
        )
        assert response.status_code == 201

    overview = client.get(f"/api/v1/esg/organizations/{organization_id}/overview")
    assert overview.status_code == 200
    assert overview.json() == {
        "organization": "Eco Industries S.A.",
        "sites": 1,
        "stakeholders": 1,
        "esg_topics": 3,
        "environmental_topics": 1,
        "social_topics": 1,
        "governance_topics": 1,
    }


def test_esg_api_validates_references_and_stakeholder_levels(client):
    assert client.get("/api/v1/esg/organizations/999/overview").status_code == 404
    invalid = client.post(
        "/api/v1/esg/organizations/999/stakeholders",
        json={
            "name": "Comunidade",
            "stakeholder_type": "community",
            "influence_level": 6,
            "impact_level": 5,
        },
    )
    assert invalid.status_code == 422
