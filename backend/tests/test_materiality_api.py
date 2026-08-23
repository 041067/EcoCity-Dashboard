from app.models.esg_topic import ESGTopic
from app.repositories.esg_topic_repository import ESGTopicRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.stakeholder_repository import StakeholderRepository


def _organization_with_topic_and_stakeholder(db_session):
    organization = OrganizationRepository(db_session).create(
        name="Eco Industries", organization_type="company", country="Brasil"
    )
    topic = ESGTopic(code="ghg-emissions", name="GHG Emissions", pillar="E", active=True)
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)
    ESGTopicRepository(db_session).create_or_update_link(organization.id, topic.id, enabled=True)
    stakeholder = StakeholderRepository(db_session).create(
        organization.id,
        name="Comunidade local",
        stakeholder_type="community",
        influence_level=4,
        impact_level=5,
    )
    return organization, topic, stakeholder


def _completed_payload(topic_id: int, stakeholder_id: int, year: int = 2026):
    return {
        "topic_id": topic_id,
        "reporting_year": year,
        "impact": {"severity": 5, "scope": 4, "likelihood": 5, "remediability": 3},
        "financial": {
            "revenue_impact": 2,
            "cost_impact": 5,
            "asset_impact": 3,
            "financing_impact": 3,
            "regulatory_impact": 4,
        },
        "stakeholders": [
            {"stakeholder_id": stakeholder_id, "relevance": 5, "concern_level": 5, "influence": 4}
        ],
        "evidences": [
            {
                "evidence_type": "stakeholder",
                "source": "Entrevista comunit\u00e1ria",
                "description": "Consulta anual de partes interessadas.",
            }
        ],
        "status": "completed",
    }


def test_materiality_api_calculates_scores_and_explains_result(client, db_session):
    organization, topic, stakeholder = _organization_with_topic_and_stakeholder(db_session)
    response = client.post(
        f"/api/v1/esg/organizations/{organization.id}/materiality",
        json=_completed_payload(topic.id, stakeholder.id),
    )

    assert response.status_code == 201
    assessment = response.json()
    assert assessment["impact_score"] == 85.0
    assert assessment["financial_score"] == 68.0
    assert assessment["stakeholder_score"] == 93.33
    assert assessment["materiality_score"] == 79.87
    assert assessment["priority_level"] == "high"
    assert assessment["status"] == "completed"
    assert assessment["impact_assessment"]["severity"] == 5
    assert len(assessment["evidences"]) == 1

    explanation = client.get(
        f"/api/v1/esg/organizations/{organization.id}/materiality/{assessment['id']}/explanation"
    )
    assert explanation.status_code == 200
    assert explanation.json()["components"] == {
        "impact": 85.0,
        "financial": 68.0,
        "stakeholder": 93.33,
    }
    assert explanation.json()["weights"] == {"impact": 0.4, "financial": 0.4, "stakeholder": 0.2}

    matrix = client.get(f"/api/v1/esg/organizations/{organization.id}/materiality/matrix")
    assert matrix.status_code == 200
    assert matrix.json()["reporting_year"] == 2026
    assert matrix.json()["assessments"][0]["topic"]["name"] == "GHG Emissions"


def test_materiality_api_rejects_client_scores_and_invalid_ownership(client, db_session):
    organization, topic, stakeholder = _organization_with_topic_and_stakeholder(db_session)
    payload = _completed_payload(topic.id, stakeholder.id)
    payload["impact_score"] = 100
    assert client.post(f"/api/v1/esg/organizations/{organization.id}/materiality", json=payload).status_code == 422

    other_organization = OrganizationRepository(db_session).create(
        name="Outra empresa", organization_type="company", country="Brasil"
    )
    assert (
        client.post(
            f"/api/v1/esg/organizations/{other_organization.id}/materiality",
            json=_completed_payload(topic.id, stakeholder.id),
        ).status_code
        == 422
    )


def test_materiality_api_preserves_history_and_locks_completed_records(client, db_session):
    organization, topic, stakeholder = _organization_with_topic_and_stakeholder(db_session)
    first = client.post(
        f"/api/v1/esg/organizations/{organization.id}/materiality",
        json=_completed_payload(topic.id, stakeholder.id, 2026),
    )
    assert first.status_code == 201
    assert (
        client.put(
            f"/api/v1/esg/organizations/{organization.id}/materiality/{first.json()['id']}",
            json={"status": "in_review"},
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/v1/esg/organizations/{organization.id}/materiality",
            json=_completed_payload(topic.id, stakeholder.id, 2026),
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/v1/esg/organizations/{organization.id}/materiality",
            json=_completed_payload(topic.id, stakeholder.id, 2027),
        ).status_code
        == 201
    )
    history = client.get(f"/api/v1/esg/organizations/{organization.id}/materiality")
    assert [item["reporting_year"] for item in history.json()] == [2027, 2026]


def test_materiality_api_requires_all_components_to_complete(client, db_session):
    organization, topic, _ = _organization_with_topic_and_stakeholder(db_session)
    response = client.post(
        f"/api/v1/esg/organizations/{organization.id}/materiality",
        json={
            "topic_id": topic.id,
            "reporting_year": 2026,
            "impact": {"severity": 5, "scope": 5, "likelihood": 5, "remediability": 5},
            "financial": {
                "revenue_impact": 5,
                "cost_impact": 5,
                "asset_impact": 5,
                "financing_impact": 5,
                "regulatory_impact": 5,
            },
            "status": "completed",
        },
    )
    assert response.status_code == 422
    assert "stakeholder" in response.json()["detail"].lower()


def test_materiality_api_completes_a_draft_after_stakeholder_assessment(client, db_session):
    organization, topic, stakeholder = _organization_with_topic_and_stakeholder(db_session)
    draft = client.post(
        f"/api/v1/esg/organizations/{organization.id}/materiality",
        json={
            "topic_id": topic.id,
            "reporting_year": 2026,
            "impact": {"severity": 4, "scope": 4, "likelihood": 4, "remediability": 4},
            "financial": {
                "revenue_impact": 4,
                "cost_impact": 4,
                "asset_impact": 4,
                "financing_impact": 4,
                "regulatory_impact": 4,
            },
            "status": "draft",
        },
    )
    assert draft.status_code == 201
    assert draft.json()["materiality_score"] is None

    stakeholder_response = client.post(
        f"/api/v1/esg/materiality/{draft.json()['id']}/stakeholders",
        json={"stakeholder_id": stakeholder.id, "relevance": 4, "concern_level": 5, "influence": 4},
    )
    assert stakeholder_response.status_code == 201
    completed = client.put(
        f"/api/v1/esg/organizations/{organization.id}/materiality/{draft.json()['id']}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["materiality_score"] == 81.33


def test_materiality_api_rejects_duplicate_stakeholders_in_one_request(client, db_session):
    organization, topic, stakeholder = _organization_with_topic_and_stakeholder(db_session)
    payload = _completed_payload(topic.id, stakeholder.id)
    payload["stakeholders"].append(payload["stakeholders"][0].copy())

    assert (
        client.post(f"/api/v1/esg/organizations/{organization.id}/materiality", json=payload).status_code
        == 422
    )
