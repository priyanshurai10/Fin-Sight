import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from src.core.config import settings

def perform_customer_rfm_segmentation(df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        if not os.path.exists(settings.PROCESSED_DATA_PATH):
            from src.services.etl import ETLPipeline
            etl = ETLPipeline()
            df = etl.run()
        else:
            df = pd.read_csv(settings.PROCESSED_DATA_PATH)
            
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    max_date = df['timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('customer_id').agg({
        'timestamp': lambda x: (max_date - x.max()).days,
        'transaction_id': 'count',
        'amount': 'sum',
        'is_fraud_actual': 'sum'
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency_days', 'frequency_cnt', 'monetary_val', 'fraud_cnt']
    
    # Standardize RFM for Clustering
    X_rfm = rfm[['recency_days', 'frequency_cnt', 'monetary_val']].copy()
    X_rfm_scaled = (X_rfm - X_rfm.mean()) / (X_rfm.std() + 1e-6)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(X_rfm_scaled)
    
    # Calculate distinct cluster metrics for human-readable labels
    cluster_summary = rfm.groupby('cluster').agg({
        'monetary_val': 'mean',
        'recency_days': 'mean',
        'frequency_cnt': 'mean',
        'fraud_cnt': 'mean'
    })
    
    # Sort clusters by monetary value and fraud density to assign distinct labels
    sorted_monetary = cluster_summary.sort_values(by='monetary_val', ascending=False).index.tolist()
    sorted_fraud = cluster_summary.sort_values(by='fraud_cnt', ascending=False).index.tolist()
    
    fraud_cluster = sorted_fraud[0]
    vip_cluster = [c for c in sorted_monetary if c != fraud_cluster][0]
    remaining = [c for c in cluster_summary.index if c not in (fraud_cluster, vip_cluster)]
    
    dormant_cluster = rfm.loc[rfm['cluster'].isin(remaining)].groupby('cluster')['recency_days'].mean().idxmax()
    standard_cluster = [c for c in remaining if c != dormant_cluster][0]
    
    labels = {
        fraud_cluster: "High Risk Fraud-Prone",
        vip_cluster: "VIP Institutional Accounts",
        dormant_cluster: "Dormant / At Risk",
        standard_cluster: "Standard Retail Accounts"
    }
            
    rfm['segment_label'] = rfm['cluster'].map(labels)
    return rfm

if __name__ == "__main__":
    res = perform_customer_rfm_segmentation()
    print("Customer Segmentation Sample:\n", res['segment_label'].value_counts())
