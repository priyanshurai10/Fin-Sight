import os
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.database import SessionLocal, engine, Base
from src.db.models import Transaction, User, CustomerSegment
from src.core.security import get_password_hash

CONTINENT_MAP = {
    "US": "North America", "CA": "North America", "MX": "North America",
    "UK": "Europe", "DE": "Europe", "FR": "Europe", "IT": "Europe", "ES": "Europe", "NL": "Europe", "CH": "Europe", "SE": "Europe",
    "JP": "Asia-Pacific", "CN": "Asia-Pacific", "KR": "Asia-Pacific", "IN": "Asia-Pacific", "SG": "Asia-Pacific", "AU": "Asia-Pacific", "HK": "Asia-Pacific",
    "BR": "Latin America", "AR": "Latin America", "CL": "Latin America", "CO": "Latin America",
    "AE": "Middle East & Africa", "SA": "Middle East & Africa", "ZA": "Middle East & Africa", "NG": "Middle East & Africa", "EG": "Middle East & Africa", "IL": "Middle East & Africa"
}

class ETLPipeline:
    def __init__(self, raw_filepath: str = settings.RAW_DATA_PATH, processed_filepath: str = settings.PROCESSED_DATA_PATH):
        self.raw_filepath = raw_filepath
        self.processed_filepath = processed_filepath

    def extract(self) -> pd.DataFrame:
        if not os.path.exists(self.raw_filepath):
            from src.data.generate_synthetic_data import generate_synthetic_transactions
            df = generate_synthetic_transactions()
        else:
            df = pd.read_csv(self.raw_filepath)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Missing values
        df['amount'] = df['amount'].fillna(df['amount'].median())
        df['distance_from_home_km'] = df['distance_from_home_km'].fillna(0.0)
        df['merchant_category'] = df['merchant_category'].fillna('Unknown')
        
        # Ensure continent column exists
        if 'continent' not in df.columns:
            df['continent'] = df['location_country'].map(CONTINENT_MAP).fillna('Global')
            
        # Time-based features
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        df['is_night_transaction'] = df['hour_of_day'].apply(lambda x: 1 if x in [0, 1, 2, 3, 4, 23] else 0)
        
        high_risk_countries = ['RU', 'CN', 'NG', 'BR', 'MX']
        high_risk_categories = ['Crypto Exchange', 'Wire Transfer', 'Jewelry & Luxury', 'Online Gaming & Betting']
        
        df['is_high_risk_country'] = df['location_country'].apply(lambda x: 1 if x in high_risk_countries else 0)
        df['is_high_risk_category'] = df['merchant_category'].apply(lambda x: 1 if x in high_risk_categories else 0)
        df['is_online_entry'] = df['entry_mode'].apply(lambda x: 1 if 'online' in str(x).lower() or 'cnp' in str(x).lower() else 0)
        
        # Customer amount Z-scores
        cust_stats = df.groupby('customer_id')['amount'].agg(['mean', 'std']).reset_index()
        cust_stats['std'] = cust_stats['std'].replace(0, 1.0).fillna(1.0)
        
        df = df.merge(cust_stats, on='customer_id', how='left')
        df['amount_zscore_cust'] = (df['amount'] - df['mean']) / df['std']
        df['amount_zscore_cust'] = df['amount_zscore_cust'].fillna(0.0)
        df.drop(columns=['mean', 'std'], inplace=True)
        
        os.makedirs(os.path.dirname(self.processed_filepath), exist_ok=True)
        df.to_csv(self.processed_filepath, index=False)
        return df

    def load_db(self, df: pd.DataFrame):
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        try:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                db.add(User(
                    username="admin",
                    email="admin@finsight.ai",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Global Platform Administrator",
                    role="admin"
                ))
                db.commit()

            existing_cnt = db.query(Transaction).count()
            if existing_cnt == 0:
                tx_records = []
                for _, row in df.head(4000).iterrows():
                    tx_records.append(Transaction(
                        transaction_id=row['transaction_id'],
                        customer_id=row['customer_id'],
                        timestamp=pd.to_datetime(row['timestamp']),
                        amount=float(row['amount']),
                        merchant_category=str(row['merchant_category']),
                        card_type=str(row['card_type']),
                        entry_mode=str(row['entry_mode']),
                        channel=str(row['channel']),
                        location_country=str(row['location_country']),
                        location_city=str(row['location_city']),
                        distance_from_home_km=float(row['distance_from_home_km']),
                        device_id=str(row['device_id']),
                        ip_address=str(row['ip_address']),
                        velocity_1h=int(row['velocity_1h']),
                        velocity_24h=int(row['velocity_24h']),
                        is_fraud_actual=bool(row['is_fraud_actual']),
                        fraud_risk_score=float(88.0 if row['is_fraud_actual'] else 6.0),
                        risk_level="CRITICAL" if row['is_fraud_actual'] else "LOW",
                        status="REJECTED" if row['is_fraud_actual'] else "APPROVED"
                    ))
                db.bulk_save_objects(tx_records)
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"DB load warning: {e}")
        finally:
            db.close()

    def run(self) -> pd.DataFrame:
        df_raw = self.extract()
        df_transformed = self.transform(df_raw)
        self.load_db(df_transformed)
        return df_transformed

if __name__ == "__main__":
    etl = ETLPipeline()
    etl.run()
