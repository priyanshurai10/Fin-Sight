import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.core.config import settings

def generate_financial_forecast(days_ahead: int = 30) -> Dict[str, Any]:
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        from src.services.etl import ETLPipeline
        etl = ETLPipeline()
        df = etl.run()
    else:
        df = pd.read_csv(settings.PROCESSED_DATA_PATH)
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    daily = df.groupby('date').agg({
        'amount': 'sum',
        'transaction_id': 'count',
        'is_fraud_actual': 'sum'
    }).reset_index()
    
    daily.columns = ['date', 'revenue', 'volume', 'fraud_cnt']
    daily = daily.sort_values(by='date').reset_index(drop=True)
    
    # Calculate historical metrics
    avg_daily_revenue = daily['revenue'].mean()
    avg_daily_volume = daily['volume'].mean()
    avg_daily_fraud = daily['fraud_cnt'].mean()
    
    # Growth rates
    recent_trend = daily.tail(14)['revenue'].mean() / (daily.head(14)['revenue'].mean() + 1e-6)
    growth_factor = np.clip(recent_trend ** (1/14), 0.98, 1.03)
    
    last_date = pd.to_datetime(daily['date'].max())
    
    forecast_records = []
    current_rev = daily['revenue'].iloc[-1]
    
    for i in range(1, days_ahead + 1):
        fc_date = last_date + timedelta(days=i)
        # Seasonality factor (weekends lower volume)
        day_weight = 0.75 if fc_date.dayofweek >= 5 else 1.10
        noise = np.random.normal(1.0, 0.05)
        
        current_rev = current_rev * growth_factor
        fc_revenue = round(float(current_rev * day_weight * noise), 2)
        fc_volume = int(max(10, avg_daily_volume * day_weight * noise))
        fc_fraud = int(max(0, round(avg_daily_fraud * day_weight * noise)))
        
        forecast_records.append({
            "date": fc_date.strftime("%Y-%m-%d"),
            "forecast_revenue": fc_revenue,
            "forecast_volume": fc_volume,
            "forecast_fraud_count": fc_fraud
        })
        
    historical_data = daily.tail(30).to_dict(orient='records')
    # Convert dates to string
    for h in historical_data:
        h['date'] = str(h['date'])
        h['revenue'] = round(float(h['revenue']), 2)
        
    return {
        "days_ahead": days_ahead,
        "historical_daily": historical_data,
        "forecast_daily": forecast_records,
        "projected_total_revenue": round(sum(r['forecast_revenue'] for r in forecast_records), 2),
        "projected_total_volume": sum(r['forecast_volume'] for r in forecast_records),
        "projected_total_fraud": sum(r['forecast_fraud_count'] for r in forecast_records)
    }

if __name__ == "__main__":
    res = generate_financial_forecast(14)
    print("Forecast Summary:\nProjected Total Revenue:", res['projected_total_revenue'])
