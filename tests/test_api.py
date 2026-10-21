"""
Integration and End-to-End Smoke Tests for BeachWaste AI API.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "compute_device" in data

def test_beaches_list():
    resp = client.get("/api/beaches")
    assert resp.status_code == 200
    beaches = resp.json()
    assert len(beaches) >= 12
    assert any(b["id"] == "beach_miami_south" for b in beaches)

def test_beach_detail():
    resp = client.get("/api/beaches/beach_bondi")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Bondi Beach, Sydney"
    assert len(data["observations"]) >= 48
    assert data["avg_monthly_waste_kg"] > 0

def test_beach_compare():
    resp = client.get("/api/beaches/compare?beach_ids=beach_bondi,beach_miami_south")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["compared_beaches"]) == 2
    assert "comparability_warning" in data

def test_forecast_generation():
    payload = {
        "beach_id": "beach_miami_south",
        "model_type": "lstm",
        "horizon_months": 6,
        "currency": "USD"
    }
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["monthly_forecasts"]) == 6
    assert data["cumulative_predicted_waste_kg"] > 0
    assert data["forecast_uncertainty_pct"] > 0

def test_cost_endpoint():
    payload = {
        "total_waste_kg": 5000.0,
        "currency": "EUR"
    }
    resp = client.post("/api/cost/estimate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["currency"] == "EUR"
    assert data["net_total_cost"] > 0

def test_models_list():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["models"]) == 3
    # Check that LSTM and Encoder-Decoder are marked trained
    assert any(m["model_type"] == "lstm" and m["is_trained"] for m in data["models"])

def test_autoencoder_anomalies():
    resp = client.get("/api/models/autoencoder/anomalies")
    assert resp.status_code == 200
    data = resp.json()
    assert "anomalies_detected_count" in data
    assert "threshold" in data

def test_datasets_sample_csv():
    resp = client.get("/api/datasets/sample.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "beach_id" in resp.text
