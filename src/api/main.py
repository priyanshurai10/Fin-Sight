import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from src.core.config import settings
from src.db.database import engine, Base
from src.api.routes import auth, transactions, analytics, ml, reports

# Safely initialize database on startup (skip disk write operations on Vercel's read-only filesystem)
try:
    Base.metadata.create_all(bind=engine)
    if not os.getenv("VERCEL"):
        from src.services.etl import ETLPipeline
        etl = ETLPipeline()
        etl.run()
except Exception as err:
    print(f"Serverless startup notice: {err}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Financial Intelligence & Fraud Analytics Platform API. Powered by Scikit-Learn, FastAPI, PostgreSQL, and OpenPyXL.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(ml.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

# Serve Static Web UI Dashboard
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
try:
    os.makedirs(static_dir, exist_ok=True)
except OSError:
    pass
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
