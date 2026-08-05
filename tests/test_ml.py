import pytest
from src.ml.predict import FraudPredictionEngine
from src.services.segmentation import perform_customer_rfm_segmentation
from src.services.forecasting import generate_financial_forecast

def test_ml_prediction():
    engine = FraudPredictionEngine()
    test_tx = {
        "transaction_id": "TXN_TEST_001",
        "amount": 4500.0,
        "merchant_category": "Crypto Exchange",
        "location_country": "RU",
        "entry_mode": "Online",
        "velocity_1h": 8,
        "distance_from_home_km": 2500.0
    }
    result = engine.predict_transaction(test_tx)
    assert "risk_score" in result
    assert result["risk_score"] > 50.0 # High risk parameters should yield high score
    assert "CRITICAL" in result["risk_level"] or "HIGH" in result["risk_level"]

def test_segmentation():
    rfm = perform_customer_rfm_segmentation()
    assert "segment_label" in rfm.columns
    assert len(rfm) > 0

def test_forecasting():
    fc = generate_financial_forecast(days_ahead=7)
    assert len(fc["forecast_daily"]) == 7
    assert fc["projected_total_revenue"] > 0
