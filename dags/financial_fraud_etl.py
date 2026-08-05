from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'finsight_data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'financial_intelligence_fraud_etl',
    default_args=default_args,
    description='Automated pipeline for financial transaction ingestion, ML fraud scoring, and executive report generation',
    schedule_interval='0 2 * * *', # Daily at 2:00 AM
    catchup=False,
)

def run_etl_task():
    from src.services.etl import ETLPipeline
    etl = ETLPipeline()
    df = etl.run()
    print(f"ETL Execution complete: Processed {len(df)} records.")

def train_ml_task():
    from src.ml.train import train_fraud_models
    metrics = train_fraud_models()
    print(f"ML Retraining complete: ROC-AUC={metrics['roc_auc']}, F1={metrics['f1_score']}")

def generate_reports_task():
    from src.reporting.excel_generator import build_executive_excel_report
    from src.reporting.pptx_generator import build_executive_pptx_report
    from src.reporting.pdf_generator import build_executive_pdf_report
    
    excel_path = build_executive_excel_report()
    pptx_path = build_executive_pptx_report()
    pdf_path = build_executive_pdf_report()
    print(f"Reports generated successfully:\n- {excel_path}\n- {pptx_path}\n- {pdf_path}")

t1 = PythonOperator(
    task_id='ingest_transform_data',
    python_callable=run_etl_task,
    dag=dag,
)

t2 = PythonOperator(
    task_id='retrain_fraud_ml_models',
    python_callable=train_ml_task,
    dag=dag,
)

t3 = PythonOperator(
    task_id='generate_c_suite_reports',
    python_callable=generate_reports_task,
    dag=dag,
)

t1 >> t2 >> t3
