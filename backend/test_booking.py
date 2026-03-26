from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_booking_search_returns_links():
    payload = {
        "origin": "Mumbai",
        "destination": "Jaipur",
        "startDate": "2026-06-01",
        "endDate": "2026-06-04",
        "adults": 2,
    }
    response = client.post("/bookings/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "links" in data
    assert "flights" in data["links"]
    assert len(data["links"]["flights"]) >= 1
    assert "live" in data
    assert "flights" in data["live"]
    assert "dummy" in data
    assert len(data["dummy"]["flights"]) == 20
    assert len(data["dummy"]["trains"]) == 20
    assert len(data["dummy"]["buses"]) == 20
    assert len(data["dummy"]["hotels"]) == 20


def test_booking_search_rejects_bad_dates():
    response = client.post(
        "/bookings/search",
        json={
            "origin": "Mumbai",
            "destination": "Jaipur",
            "startDate": "2026-06-10",
            "endDate": "2026-06-01",
            "adults": 1,
        },
    )
    assert response.status_code == 422
