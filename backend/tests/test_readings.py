def test_latest_readings_empty(client):
    response = client.get("/api/v1/readings/latest")
    assert response.status_code == 200
    assert response.json() == []


def test_readings_history_empty(client):
    response = client.get("/api/v1/readings/history")
    assert response.status_code == 200
    assert response.json() == []
