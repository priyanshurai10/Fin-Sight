import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.core.config import settings
from src.ml.feature_engineering import prepare_feature_matrix

class FraudPredictionEngine:
    def __init__(self, model_path: str = os.path.join(settings.MODEL_DIR, "fraud_model.joblib")):
        self.model_path = model_path
        self.model_artifact = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model_artifact = joblib.load(self.model_path)
        else:
            print("Model file not found. Triggering initial training...")
            from src.ml.train import train_fraud_models
            train_fraud_models()
            self.model_artifact = joblib.load(self.model_path)

    def predict_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        df_single = pd.DataFrame([transaction_data])
        
        # Calculate calculated features if missing
        if 'timestamp' in df_single.columns:
            ts = pd.to_datetime(df_single['timestamp'].iloc[0])
            df_single['hour_of_day'] = ts.hour
            df_single['day_of_week'] = ts.dayofweek
            df_single['is_weekend'] = 1 if ts.dayofweek >= 5 else 0
            df_single['is_night_transaction'] = 1 if ts.hour in [0,1,2,3,4,23] else 0
        else:
            df_single['hour_of_day'] = 12
            df_single['is_weekend'] = 0
            df_single['is_night_transaction'] = 0
            
        high_risk_countries = ['RU', 'CN', 'NG']
        high_risk_categories = ['Crypto Exchange', 'Wire Transfer', 'Jewelry']
        
        country = str(df_single.get('location_country', pd.Series(['US'])).iloc[0])
        category = str(df_single.get('merchant_category', pd.Series(['Grocery'])).iloc[0])
        entry = str(df_single.get('entry_mode', pd.Series(['Chip'])).iloc[0])
        
        df_single['is_high_risk_country'] = 1 if country in high_risk_countries else 0
        df_single['is_high_risk_category'] = 1 if category in high_risk_categories else 0
        df_single['is_online_entry'] = 1 if entry.lower() == 'online' else 0
        df_single['amount_zscore_cust'] = float(df_single.get('amount_zscore_cust', pd.Series([1.0])).iloc[0])

        X_input = prepare_feature_matrix(df_single)
        
        pipeline = self.model_artifact['pipeline']
        iso_forest = self.model_artifact['iso_forest']
        preprocessor = self.model_artifact['preprocessor']
        
        # Supervised probability
        prob = float(pipeline.predict_proba(X_input)[0, 1])
        risk_score = round(prob * 100, 1)
        
        # Anomaly score from Isolation Forest
        X_proc = preprocessor.transform(X_input)
        anomaly_score = float(-iso_forest.score_samples(X_proc)[0])
        
        # Determine Risk Level
        if risk_score >= 75.0 or anomaly_score > 0.65:
            risk_level = "CRITICAL"
            status = "REJECTED"
        elif risk_score >= 45.0:
            risk_level = "HIGH"
            status = "FLAGGED"
        elif risk_score >= 20.0:
            risk_level = "MEDIUM"
            status = "UNDER_REVIEW"
        else:
            risk_level = "LOW"
            status = "APPROVED"

        # Key Risk Factors Analysis
        risk_factors: List[str] = []
        amount = float(df_single['amount'].iloc[0])
        v1h = int(df_single.get('velocity_1h', pd.Series([1])).iloc[0])
        v24h = int(df_single.get('velocity_24h', pd.Series([1])).iloc[0])
        dist = float(df_single.get('distance_from_home_km', pd.Series([0])).iloc[0])
        
        if amount > 1000:
            risk_factors.append(f"High Transaction Amount (${amount:,.2f})")
        if v1h >= 4 or v24h >= 12:
            risk_factors.append(f"Rapid Transaction Velocity Spike ({v1h} in 1h, {v24h} in 24h)")
        if country in high_risk_countries:
            risk_factors.append(f"High-Risk Geolocation Jurisdiction ({country})")
        if category in high_risk_categories:
            risk_factors.append(f"High-Risk Merchant Category ({category})")
        if dist > 200:
            risk_factors.append(f"Substantial Distance From Primary Location ({dist} km)")
        if df_single['is_night_transaction'].iloc[0] == 1:
            risk_factors.append("Off-Hours / Midnight Activity Window")
        if not risk_factors:
            risk_factors.append("Standard Customer Behavioral Profile")

        return {
            "transaction_id": str(df_single.get('transaction_id', pd.Series(['TXN_SIMULATED'])).iloc[0]),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "status": status,
            "fraud_probability": round(prob, 4),
            "anomaly_score": round(anomaly_score, 4),
            "risk_factors": risk_factors
        }

if __name__ == "__main__":
    engine = FraudPredictionEngine()
    test_tx = {
        "transaction_id": "TXN_TEST_99",
        "customer_id": "CUST_001",
        "timestamp": "2026-08-05 02:15:00",
        "amount": 2850.0,
        "merchant_category": "Crypto Exchange",
        "card_type": "Visa Premier",
        "entry_mode": "Online",
        "channel": "Web Browser",
        "location_country": "RU",
        "distance_from_home_km": 3500.0,
        "velocity_1h": 6,
        "velocity_24h": 18
    }
    res = engine.predict_transaction(test_tx)
    print("Test Prediction Output:\n", res)
