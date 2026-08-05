# REST API Documentation — FinSight AI

The FinSight AI API allows real-time transaction scoring, batch ingestion, analytics querying, and automated report exports.

---

## Base URL
`http://localhost:8000/api/v1`

---

## Key API Endpoints

### 1. Authentication
- **`POST /auth/login`**: Authenticate user and obtain JWT access token.
- **`POST /auth/register`**: Register new platform user (Roles: `admin`, `analyst`, `auditor`).

### 2. Transactions
- **`GET /transactions`**: Query transactions with pagination and risk filtering (`fraud_only=true`, `country=US`).
- **`POST /transactions/upload-csv`**: Batch ingest CSV transactions into the ETL pipeline.

### 3. Analytics & Intelligence
- **`GET /analytics/kpis`**: Fetch system-wide KPI summary (Volume, Fraud Rate, Exposure, Channel Breakdown).
- **`GET /analytics/segmentation`**: Retrieve RFM customer cluster metrics and profiles.
- **`GET /analytics/forecasting?days=30`**: Get projected revenue and fraud volume time-series trends.

### 4. Machine Learning & Risk Intelligence
- **`POST /ml/score`**: Real-time transaction risk scoring with SHAP factor explanation.
- **`POST /ml/retrain`**: Trigger online model retraining pipeline.

### 5. Automated Reports
- **`GET /reports/excel`**: Download formatted Executive Excel Workbook (`.xlsx`).
- **`GET /reports/pptx`**: Download C-Suite PowerPoint Presentation Deck (`.pptx`).
- **`GET /reports/pdf`**: Download Executive PDF Summary (`.pdf`).
