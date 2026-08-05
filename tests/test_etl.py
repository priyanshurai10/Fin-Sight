import os
import pandas as pd
import pytest
from src.services.etl import ETLPipeline
from src.data.generate_synthetic_data import generate_synthetic_transactions

def test_synthetic_generator():
    df = generate_synthetic_transactions(num_records=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    assert 'transaction_id' in df.columns
    assert 'is_fraud_actual' in df.columns

def test_etl_transform(tmp_path):
    raw_csv = os.path.join(tmp_path, "test_raw.csv")
    proc_csv = os.path.join(tmp_path, "test_proc.csv")
    
    df_raw = generate_synthetic_transactions(num_records=50)
    df_raw.to_csv(raw_csv, index=False)
    
    etl = ETLPipeline(raw_filepath=raw_csv, processed_filepath=proc_csv)
    df_proc = etl.run()
    
    assert len(df_proc) == 50
    assert 'hour_of_day' in df_proc.columns
    assert 'amount_zscore_cust' in df_proc.columns
