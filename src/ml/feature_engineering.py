import pandas as pd
import numpy as np

NUMERICAL_FEATURES = [
    'amount', 'distance_from_home_km', 'velocity_1h', 'velocity_24h',
    'hour_of_day', 'is_weekend', 'is_night_transaction',
    'is_high_risk_country', 'is_high_risk_category', 'is_online_entry',
    'amount_zscore_cust'
]

CATEGORICAL_FEATURES = ['merchant_category', 'card_type', 'entry_mode', 'channel']

FEATURE_COLS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

def prepare_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = df.copy()
    
    # Fill defaults if missing
    for col in NUMERICAL_FEATURES:
        if col not in df_feat.columns:
            df_feat[col] = 0
        df_feat[col] = df_feat[col].fillna(0)
        
    for col in CATEGORICAL_FEATURES:
        if col not in df_feat.columns:
            df_feat[col] = 'Unknown'
        df_feat[col] = df_feat[col].fillna('Unknown')
        
    return df_feat[FEATURE_COLS]
