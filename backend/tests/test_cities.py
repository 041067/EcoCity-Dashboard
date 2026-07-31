from app.models.city import City


def test_list_cities_empty(client):
    response = client.get("/api/v1/cities")
    assert response.status_code == 200
    assert response.json() == []


def test_list_cities_with_data(client, db_session):
    db_session.add(
        City(
            name="São Paulo",
            state="SP",
            latitude=-23.55,
            longitude=-46.63,
        )
    )
    db_session.commit()

    response = client.get("/api/v1/cities")
    assert response.status_code == 200
    cities = response.json()
    assert len(cities) == 1
    assert cities[0]["name"] == "São Paulo"
