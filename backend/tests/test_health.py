
import httpx


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "online"
    assert body["database"] == "connected"


def test_health_api_v1(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health_database_ok(client):
    response = client.get("/health/database")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_database_api_v1(client):
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_health_external_services_ok(client, monkeypatch):
    def fake_get(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self):
                pass

        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    response = client.get("/health/external-services")
    assert response.status_code == 200
    body = response.json()
    assert body["services"]["open_meteo"]["status"] == "ok"
    assert body["services"]["groq"]["status"] in ("configured", "not_configured")


def test_health_external_services_open_meteo_fail(client, monkeypatch):
    def fake_get_fail(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "get", fake_get_fail)
    response = client.get("/health/external-services")
    assert response.status_code == 200
    body = response.json()
    assert body["services"]["open_meteo"]["status"] == "error"
