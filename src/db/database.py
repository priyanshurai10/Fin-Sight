import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Ensure data directory exists
try:
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.DATA_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(settings.DATA_DIR, "processed"), exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
except OSError:
    pass  # Serverless environments like Vercel have read-only filesystems

# Prefer SQLite for quick zero-config local run, allow Postgres override
db_url = settings.POSTGRES_URL if settings.POSTGRES_URL else settings.SQLITE_URL
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
