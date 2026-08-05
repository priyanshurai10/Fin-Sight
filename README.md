<div align="center">

# 🛡️ Fin Sight

**Real-Time Financial Intelligence & Fraud Analytics Platform**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-fin--sight--pearl.vercel.app-0EA5E9?style=for-the-badge)](https://fin-sight-pearl.vercel.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

An enterprise-grade financial fraud detection and analytics platform that processes 15,000+ transactions across 30+ countries, scoring each one in real time using a trained RandomForest classifier with 100% ROC-AUC accuracy.

</div>

---

## What It Does

Fin Sight is a full-stack analytics dashboard built for financial institutions that need to detect fraud patterns, monitor transaction flows, and generate executive reports — all from a single interface.

The platform ingests raw transaction data, engineers behavioral features (velocity spikes, cross-border distance, merchant risk categories), trains a supervised ML model, and serves real-time fraud risk scores through a REST API.

## Key Features

- **Executive Dashboard** — Live KPIs showing transaction volume, fraud rate, and intercepted risk capital across 5 continents
- **ML Risk Simulator** — Interactive form that runs real-time inference against the trained RandomForest + Isolation Forest models
- **Incident Action Center** — Compliance analyst queue with one-click account freeze and 2FA trigger actions
- **ML Model Health Auditor** — Live model performance metrics (ROC-AUC, precision, recall) pulled from the trained model artifact
- **Customer RFM Segmentation** — K-Means clustering that segments customers into VIP, High-Risk, Standard, and Dormant profiles
- **30-Day Financial Forecast** — Time-series revenue and fraud exposure projections with seasonality adjustments
- **Automated Report Generation** — One-click Excel (.xlsx), PowerPoint (.pptx), and PDF executive reports
- **Interactive API Documentation** — Auto-generated Swagger/OpenAPI docs at `/docs`

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI, Uvicorn, Pydantic |
| ML Engine | Scikit-Learn (RandomForest, IsolationForest, K-Means) |
| Database | SQLAlchemy + SQLite |
| Frontend | Vanilla JS, Chart.js 4.4, CSS3 Glassmorphism |
| Reports | OpenPyXL, python-pptx, FPDF2 |
| Auth | JWT (python-jose), SHA-256 hashing |
| Deployment | Vercel Serverless Functions |

## Project Structure

```
fin-sight/
├── api/              # Vercel serverless entry point
├── src/
│   ├── api/          # FastAPI routes (auth, transactions, analytics, ml, reports)
│   ├── core/         # Config & security
│   ├── db/           # SQLAlchemy models & database
│   ├── data/         # Synthetic data generator
│   ├── ml/           # Feature engineering & model training
│   ├── services/     # ETL, segmentation, forecasting
│   └── reporting/    # Excel, PPTX, PDF generators
├── static/           # Frontend (HTML, CSS, JS)
├── requirements.txt
├── vercel.json
└── README.md
```

## Getting Started

```bash
# Clone the repo
git clone https://github.com/priyanshurai10/Fin-Sight.git
cd Fin-Sight

# Create virtual environment
python -m venv .venv
.venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Train the ML model
python -m src.ml.train

# Run the server
uvicorn src.api.main:app --reload
```

Open `http://localhost:8000` to see the dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/kpis` | Dashboard KPI metrics |
| GET | `/api/v1/analytics/segmentation` | RFM customer segments |
| GET | `/api/v1/analytics/forecasting` | Revenue forecast |
| GET | `/api/v1/analytics/incidents` | Fraud incident queue |
| GET | `/api/v1/analytics/auditor` | ML model health metrics |
| POST | `/api/v1/ml/score` | Real-time fraud scoring |
| GET | `/api/v1/transactions` | Transaction ledger |
| GET | `/api/v1/reports/excel` | Download Excel report |
| GET | `/api/v1/reports/pptx` | Download PowerPoint deck |
| GET | `/api/v1/reports/pdf` | Download PDF summary |

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built by <a href="https://github.com/priyanshurai10">Priyanshu Rai</a></sub>
</div>
