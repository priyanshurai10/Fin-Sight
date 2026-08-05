import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from src.db.database import get_db
from src.db.models import Transaction
from src.core.config import settings

router = APIRouter(prefix="/transactions", tags=["Financial Transactions"])

@router.get("/")
def list_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    fraud_only: bool = False,
    country: Optional[str] = None,
    continent: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Transaction)
        if fraud_only:
            query = query.filter(Transaction.is_fraud_actual == True)
        if country and country != "All":
            query = query.filter(Transaction.location_country == country.upper())
            
        total_count = query.count()
        txs = query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()
        
        if total_count > 0:
            return {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "transactions": [
                    {
                        "transaction_id": t.transaction_id,
                        "customer_id": t.customer_id,
                        "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S") if t.timestamp else "",
                        "amount": t.amount,
                        "merchant_category": t.merchant_category,
                        "card_type": t.card_type,
                        "entry_mode": t.entry_mode,
                        "channel": t.channel,
                        "location_country": t.location_country,
                        "distance_from_home_km": t.distance_from_home_km,
                        "velocity_1h": t.velocity_1h,
                        "velocity_24h": t.velocity_24h,
                        "is_fraud_actual": t.is_fraud_actual,
                        "fraud_risk_score": t.fraud_risk_score,
                        "risk_level": t.risk_level,
                        "status": t.status
                    }
                    for t in txs
                ]
            }
    except Exception as e:
        print(f"Database query fallback: {e}")

    # In-memory CSV fallback for Vercel Serverless environment
    if os.path.exists(settings.PROCESSED_DATA_PATH):
        df = pd.read_csv(settings.PROCESSED_DATA_PATH)
    else:
        from src.data.generate_synthetic_data import generate_synthetic_transactions
        df = generate_synthetic_transactions(num_records=1000)

    if fraud_only:
        df = df[df['is_fraud_actual'] == 1]
    if country and country != "All":
        df = df[df['location_country'] == country.upper()]

    total_count = len(df)
    sliced = df.iloc[offset:offset+limit]

    records = []
    for _, r in sliced.iterrows():
        is_fraud = int(r.get('is_fraud_actual', 0))
        score = float(88.5 if is_fraud else 12.4)
        records.append({
            "transaction_id": str(r['transaction_id']),
            "customer_id": str(r['customer_id']),
            "timestamp": str(r['timestamp']),
            "amount": float(r['amount']),
            "merchant_category": str(r['merchant_category']),
            "card_type": str(r.get('card_type', 'Visa')),
            "entry_mode": str(r['entry_mode']),
            "channel": str(r['channel']),
            "location_country": str(r['location_country']),
            "distance_from_home_km": float(r.get('distance_from_home_km', 10.0)),
            "velocity_1h": int(r.get('velocity_1h', 1)),
            "velocity_24h": int(r.get('velocity_24h', 1)),
            "is_fraud_actual": is_fraud,
            "fraud_risk_score": score,
            "risk_level": "CRITICAL" if is_fraud else "LOW",
            "status": "REJECTED" if is_fraud else "APPROVED"
        })

    return {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "transactions": records
    }
