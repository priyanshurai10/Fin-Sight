# Power BI Integration Guide — FinSight AI

This guide details how to build and connect an interactive Power BI report to the **FinSight AI** platform.

---

## 1. Data Connection Methods

### Option A: Web API Connection (Live Streaming REST API)
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Web**.
3. Select **Advanced** and enter the URL:
   `http://localhost:8000/api/v1/transactions?limit=5000`
4. Open **Power Query Editor**, click **Advanced Editor**, and paste the code from [`power_query.m`](file:///c:/Users/priya/.gemini/antigravity/scratch/FinSight%20AI/powerbi/power_query.m).

### Option B: Direct Database Connection (PostgreSQL)
1. Select **Get Data** -> **PostgreSQL Database**.
2. Server: `localhost:5432` | Database: `finsight`
3. Enter credentials and select tables: `transactions`, `users`, `customer_segments`.

---

## 2. Modeling & DAX Measures

1. Import all measures from [`dax_measures.dax`](file:///c:/Users/priya/.gemini/antigravity/scratch/FinSight%20AI/powerbi/dax_measures.dax).
2. Create a 1-to-Many Relationship between `Calendar[Date]` and `Transactions[timestamp]`.

---

## 3. Recommended Visualizations Layout

- **Card 1**: `Total Transaction Volume` ($)
- **Card 2**: `Fraud Incident Count`
- **Card 3**: `System Fraud Rate %` (Color Alert Conditional Formatting)
- **Clustered Bar Chart**: `Total Transaction Volume` vs `Fraud Monetary Exposure` by `merchant_category`
- **Donut Chart**: `Transactions Count` by `channel`
- **Line Chart**: 30-Day Moving Average Volume vs Daily Revenue Trend
- **Decomposition Tree**: Drilldown from `location_country` -> `merchant_category` -> `risk_level`
