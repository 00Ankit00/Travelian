from fastapi.testclient import TestClient

import main
from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "timestamp" in payload


def test_travel_plan_validation_rejects_invalid_dates():
    bad_payload = {
        "origin": "Mumbai",
        "destination": "Delhi",
        "startDate": "2026-02-10",
        "endDate": "2026-02-09",
        "duration": 1,
        "budget": "Moderate (₹10,000 - ₹25,000)",
        "travelStyle": "Solo Travel",
        "interests": ["Culture & Heritage"],
    }
    response = client.post("/travel/plan", json=bad_payload)
    assert response.status_code == 422


def test_chatbot_validation_rejects_empty_message():
    response = client.post("/chatbot/ask", json={"message": ""})
    assert response.status_code == 422


def test_travel_plan_returns_structured_schema(monkeypatch):
    payload = {
        "origin": "Mumbai",
        "destination": "Jaipur",
        "startDate": "2026-02-01",
        "endDate": "2026-02-04",
        "duration": 3,
        "budget": "Moderate (₹10,000 - ₹25,000)",
        "travelStyle": "Solo Travel",
        "interests": ["Culture & Heritage"],
    }

    monkeypatch.setattr(main, "TRAVEL_MODULE_AVAILABLE", True)
    monkeypatch.setattr(main, "run_task", lambda *args, **kwargs: "sample itinerary text")
    monkeypatch.setattr(
        main,
        "build_map_data",
        lambda *_: main.MapData(
            origin=main.RoutePoint(name="Mumbai", lat=19.076, lon=72.8777),
            destination=main.RoutePoint(name="Jaipur", lat=26.9124, lon=75.7873),
            routeUrl="https://www.openstreetmap.org/directions",
            googleMapsDirectionsUrl="https://www.google.com/maps/dir/19.076,72.8777/26.9124,75.7873",
            openStreetMapDirectionsUrl="https://www.openstreetmap.org/directions",
            openStreetMapEmbedUrl="https://www.openstreetmap.org/export/embed.html",
        ),
    )

    response = client.post("/travel/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "itinerary" in data
    assert isinstance(data["itinerary"]["days"], list)
    assert "map" in data
    assert data["map"]["origin"]["name"] == "Mumbai"
    assert data["budget"]["party_size"] == 1
    assert data["budget"]["trip_days"] == 3
    assert data["budget"]["per_person_total"] == 18000
    assert data["budget"]["total_budget"] == 18000


def test_travel_plan_budget_scales_with_duration(monkeypatch):
    payload = {
        "origin": "Mumbai",
        "destination": "Jaipur",
        "startDate": "2026-02-01",
        "endDate": "2026-02-07",
        "duration": 6,
        "budget": "Moderate (₹10,000 - ₹25,000)",
        "travelStyle": "Solo Travel",
        "interests": ["Culture & Heritage"],
    }

    monkeypatch.setattr(main, "TRAVEL_MODULE_AVAILABLE", True)
    monkeypatch.setattr(main, "run_task", lambda *args, **kwargs: "sample itinerary text")
    monkeypatch.setattr(
        main,
        "build_map_data",
        lambda *_: main.MapData(
            origin=main.RoutePoint(name="Mumbai", lat=19.076, lon=72.8777),
            destination=main.RoutePoint(name="Jaipur", lat=26.9124, lon=75.7873),
            routeUrl="https://www.openstreetmap.org/directions",
            googleMapsDirectionsUrl="https://www.google.com/maps/dir/19.076,72.8777/26.9124,75.7873",
            openStreetMapDirectionsUrl="https://www.openstreetmap.org/directions",
            openStreetMapEmbedUrl="https://www.openstreetmap.org/export/embed.html",
        ),
    )

    response = client.post("/travel/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["budget"]["trip_days"] == 6
    assert data["budget"]["per_person_total"] == 36000
    assert data["budget"]["total_budget"] == 36000


def test_travel_plan_budget_scales_with_group_size(monkeypatch):
    payload = {
        "origin": "Mumbai",
        "destination": "Jaipur",
        "startDate": "2026-02-01",
        "endDate": "2026-02-04",
        "duration": 3,
        "budget": "Moderate (₹10,000 - ₹25,000)",
        "travelStyle": "Group Adventure",
        "interests": ["Culture & Heritage"],
        "travelContext": {"groupSize": 10, "fitnessLevel": "Moderate"},
    }

    monkeypatch.setattr(main, "TRAVEL_MODULE_AVAILABLE", True)
    monkeypatch.setattr(main, "run_task", lambda *args, **kwargs: "sample itinerary text")
    monkeypatch.setattr(
        main,
        "build_map_data",
        lambda *_: main.MapData(
            origin=main.RoutePoint(name="Mumbai", lat=19.076, lon=72.8777),
            destination=main.RoutePoint(name="Jaipur", lat=26.9124, lon=75.7873),
            routeUrl="https://www.openstreetmap.org/directions",
            googleMapsDirectionsUrl="https://www.google.com/maps/dir/19.076,72.8777/26.9124,75.7873",
            openStreetMapDirectionsUrl="https://www.openstreetmap.org/directions",
            openStreetMapEmbedUrl="https://www.openstreetmap.org/export/embed.html",
        ),
    )

    response = client.post("/travel/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["budget"]["party_size"] == 10
    assert data["budget"]["trip_days"] == 3
    assert data["budget"]["per_person_total"] == 18000
    assert data["budget"]["total_budget"] == 180000
