# Fin Sight — Financial Intelligence & Fraud Detection Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Fin Sight is a real-time financial intelligence and fraud detection analytics platform built to ingest multi-channel transaction streams, evaluate fraud probabilities using machine learning models, and deliver executive-level business reporting.

It combines a supervised **XGBoost Classifier** (trained on historical transaction velocity and geolocation anomalies) with an unsupervised **Isolation Forest** detector (for zero-day anomaly discovery) to provide real-time risk scoring (< 25ms latency) across global transaction feeds.

---

## Key Features

- **Hybrid Machine Learning Engine**: Combines supervised XGBoost probability scoring with unsupervised Isolation Forest zero-day anomaly detection.
- **Sub-Second Ingestion & Scoring API**: Built with FastAPI, returning real-time risk scores, risk tier classifications (`CRITICAL`, `HIGH`, `ELEVATED`, `LOW`), and SHAP feature drivers.
- **Multi-Continent Geolocation Risk Matrix**: Ingests transactions across 30+ countries in 5 continents with ISO 4217 currencies and SWIFT BIC banking identifiers.
- **Automated C-Suite Reporting Suite**: Programmatically generates formatted Excel workbooks (`.xlsx`), 16:9 dark executive PowerPoint decks (`.pptx`), and PDF summary briefings (`.pdf`).
- **Analyst Incident Action Queue**: One-click SAR filing, account freeze triggers, and step-up 2FA request workflows.
- **SHAP Feature Importance & Model Auditor**: Global feature weight breakdown and cross-validated ROC-AUC model health metrics.
- **RFM Customer Segmentation**: K-Means clustering of customer accounts by recency, frequency, monetary value, and risk exposure.

---

## System Architecture

```
                               ┌───────────────────────────┐
                               │  Global Transaction Feed  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  ETL & Feature Pipelines  │
                               │  (Velocity, Z-Score, MCC) │
                               └─────────────┬─────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
                       ▼                                           ▼
          ┌─────────────────────────┐                 ┌─────────────────────────┐
          │   Supervised XGBoost    │                 │   Unsupervised Forest   │
          │   Fraud Risk Model      │                 │    Anomaly Detector     │
          └────────────┬────────────┘                 └────────────┬────────────┘
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   FastAPI Analytics Core  │
                               └─────────────┬─────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               │                             │                             │
               ▼                             ▼                             ▼
   ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
   │ Interactive Web UI   │      │ Automated Reports    │      │ REST API Specs       │
   │ (Chart.js / Glass)   │      │ (Excel, PPTX, PDF)   │      │ (Swagger / OpenAPI)  │
   └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

---

## Directory Structure

```
FinSight AI/
├── data/
│   ├── raw/                       # Raw financial transactions CSV
│   └── processed/                 # Cleaned relational SQLite database
├── src/
│   ├── api/                       # FastAPI routes & endpoints
│   ├── core/                      # Configuration, security & database sessions
│   ├── data/                      # Synthetic IEEE/PaySim data generator
│   ├── ml/                        # XGBoost & Isolation Forest training pipelines
│   └── services/                  # ETL, RFM segmentation, forecasting & reporting
├── static/                        # Frontend CSS, Chart.js & JavaScript modules
├── tests/                         # Pytest test suite
├── Dockerfile                     # Production container spec
├── docker-compose.yml             # Microservice orchestration spec
└── requirements.txt               # Python dependencies
```

---

## Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested up to Python 3.14)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/fin-sight.git
cd fin-sight
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Data & Train ML Models
```bash
# Generate 15,000 transaction records
python -m src.data.generate_synthetic_data

# Run ETL pipeline to load database
python -m src.services.etl

# Train XGBoost & Isolation Forest models
python -m src.ml.train
```

### 4. Run Live Web Server
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at `http://localhost:8000` to access the live dashboard.

---

## Git Workflow & Commands for Development

When contributing or updating the platform codebase, follow standard git feature branch workflows:

```bash
# Check repository status
git status

# Create and checkout a new feature branch
git checkout -b feature/model-optimization

# Stage your modified files
git add src/ml/train.py static/js/app.js

# Commit changes with descriptive messages
git commit -m "feat(ml): optimize XGBoost hyperparameters and update SHAP chart rendering"

# Push branch to remote GitHub repository
git push origin feature/model-optimization

# Merge into main branch
git checkout main
git merge feature/model-optimization
git push origin main
```

---

## Running Automated Tests

Run the complete pytest test suite:

```bash
pytest tests/ -v
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
