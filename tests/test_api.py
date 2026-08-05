import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_kpi_analytics():
    response = client.get("/api/v1/analytics/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_volume" in data
    assert "fraud_count" in data

def test_ml_score_endpoint():
    payload = {
        "amount": 150.0,
        "merchant_category": "Grocery",
        "location_country": "US",
        "entry_mode": "Chip",
        "velocity_1h": 1,
        "distance_from_home_km": 5.0
    }
    response = client.post("/api/v1/ml/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
