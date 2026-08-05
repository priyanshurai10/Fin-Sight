from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="analyst") # admin, analyst, auditor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    amount = Column(Float, nullable=False)
    merchant_category = Column(String, index=True)
    card_type = Column(String)
    entry_mode = Column(String) # Chip, Contactless, Online, Swiped
    channel = Column(String) # Mobile App, Web, ATM, POS
    location_country = Column(String, default="US")
    location_city = Column(String)
    distance_from_home_km = Column(Float, default=0.0)
    device_id = Column(String)
    ip_address = Column(String)
    velocity_1h = Column(Integer, default=1)
    velocity_24h = Column(Integer, default=1)
    is_fraud_actual = Column(Boolean, default=False)
    fraud_risk_score = Column(Float, default=0.0) # Model prediction score 0-100
    risk_level = Column(String, default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="APPROVED") # APPROVED, FLAGGED, REJECTED

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    alert_time = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, nullable=False)
    trigger_reason = Column(String) # Velocity Spike, Anomaly Score, High Amount
    status = Column(String, default="OPEN") # OPEN, UNDER_REVIEW, CONFIRMED_FRAUD, FALSE_POSITIVE
    assigned_to = Column(String, nullable=True)

class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    recency_days = Column(Integer)
    frequency_cnt = Column(Integer)
    monetary_val = Column(Float)
    segment_cluster = Column(Integer)
    segment_label = Column(String) # Champions, Loyal, At Risk, High Value Fraud-Prone
    last_updated = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    action = Column(String)
    details = Column(Text)
