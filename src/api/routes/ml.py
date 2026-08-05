from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.ml.predict import FraudPredictionEngine
from src.ml.train import train_fraud_models

router = APIRouter(prefix="/ml", tags=["Machine Learning & Risk Intelligence"])

prediction_engine = FraudPredictionEngine()

class TransactionScoreRequest(BaseModel):
    transaction_id: Optional[str] = "TXN_SIMULATED"
    customer_id: Optional[str] = "CUST_001"
    timestamp: Optional[str] = "2026-08-05 14:30:00"
    amount: float
    merchant_category: str
    card_type: Optional[str] = "Visa Premier"
    entry_mode: Optional[str] = "Online"
    channel: Optional[str] = "Web Browser"
    location_country: Optional[str] = "US"
    distance_from_home_km: Optional[float] = 12.5
    velocity_1h: Optional[int] = 1
    velocity_24h: Optional[int] = 3

@router.post("/score")
def score_transaction(req: TransactionScoreRequest):
    data_dict = req.dict()
    res = prediction_engine.predict_transaction(data_dict)
    return res

@router.post("/retrain")
def trigger_model_retrain():
    metrics = train_fraud_models()
    # Reload engine model
    prediction_engine._load_model()
    return {
        "message": "Fraud Machine Learning model successfully retrained and reloaded into memory.",
        "metrics": metrics
    }
