import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "FinSight AI - Financial Intelligence & Fraud Analytics Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "finsight_ai_super_secret_enterprise_jwt_key_2026_x89f2a")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database URIs
    SQLITE_URL: str = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/finsight.db'))}"
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/finsight_docs")
    
    # Data Paths
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    RAW_DATA_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw/financial_transactions.csv"))
    PROCESSED_DATA_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/cleaned_features.csv"))
    MODEL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ml/models"))
    REPORTS_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../reports/output"))

settings = Settings()
