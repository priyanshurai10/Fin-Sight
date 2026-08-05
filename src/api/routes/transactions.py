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
    query = db.query(Transaction)
    if fraud_only:
        query = query.filter(Transaction.is_fraud_actual == True)
    if country and country != "All":
        query = query.filter(Transaction.location_country == country.upper())
        
    total_count = query.count()
    txs = query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()
    
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
