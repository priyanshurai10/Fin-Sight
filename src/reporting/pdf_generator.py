import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from src.core.config import settings

class FinSightPDFReport(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42) # Slate 900
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FinSight AI -- Executive Financial Intelligence Report', 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential -- Financial Intelligence & Fraud Analytics', 0, 0, 'C')

def build_executive_pdf_report(output_filename: str = "FinSight_Executive_Summary.pdf") -> str:
    output_path = os.path.join(settings.REPORTS_DIR, output_filename)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        from src.services.etl import ETLPipeline
        etl = ETLPipeline()
        df = etl.run()
    else:
        df = pd.read_csv(settings.PROCESSED_DATA_PATH)
        
    pdf = FinSightPDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, f"Executive Summary Briefing -- {datetime.now().strftime('%B %d, %Y')}", 0, 1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 6, "This report provides a strategic overview of system-wide transaction volume, detected fraud anomalies, risk metrics, and machine learning model efficacy for the enterprise financial intelligence platform.")
    pdf.ln(5)
    
    # Key Stats Table
    total_tx = len(df)
    total_vol = float(df['amount'].sum())
    fraud_cnt = int(df['is_fraud_actual'].sum())
    fraud_rate = (fraud_cnt / total_tx) * 100 if total_tx > 0 else 0
    fraud_exposure = float(df[df['is_fraud_actual'] == 1]['amount'].sum())
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(90, 8, "Metric Parameter", 1, 0, "L", True)
    pdf.cell(90, 8, "Value", 1, 1, "R", True)
    
    pdf.set_font("Helvetica", "", 10)
    metrics_data = [
        ("Total Ingested Volume", f"${total_vol:,.2f}"),
        ("Total Transactions Processed", f"{total_tx:,}"),
        ("Confirmed Fraud Instances", f"{fraud_cnt:,}"),
        ("System Fraud Rate", f"{fraud_rate:.2f}%"),
        ("Intercepted Capital Risk", f"${fraud_exposure:,.2f}")
    ]
    
    for label, val in metrics_data:
        pdf.cell(90, 8, label, 1, 0, "L")
        pdf.cell(90, 8, val, 1, 1, "R")
        
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Risk Mitigation Guidelines", 0, 1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "1. Enforce automated step-up 2FA for all online transactions originating from non-domestic IP ranges.\n2. Retrain Random Forest models on a daily schedule using Airflow DAGs.\n3. Integrate live WebSocket alerts into corporate security operations centers.")

    pdf.output(output_path)
    print(f"Generated Executive PDF Report -> {output_path}")
    return output_path

if __name__ == "__main__":
    build_executive_pdf_report()
