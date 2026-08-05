import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.core.config import settings
from src.reporting.excel_generator import build_executive_excel_report
from src.reporting.pptx_generator import build_executive_pptx_report
from src.reporting.pdf_generator import build_executive_pdf_report

router = APIRouter(prefix="/reports", tags=["Automated Executive Reporting"])

@router.get("/excel")
def download_excel_report():
    excel_path = os.path.join(settings.REPORTS_DIR, "FinSight_Executive_Financial_Report.xlsx")
    if not os.path.exists(excel_path):
        excel_path = build_executive_excel_report()
    return FileResponse(
        path=excel_path,
        filename="FinSight_Executive_Financial_Report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/pptx")
def download_pptx_report():
    pptx_path = os.path.join(settings.REPORTS_DIR, "FinSight_Executive_Presentation.pptx")
    if not os.path.exists(pptx_path):
        pptx_path = build_executive_pptx_report()
    return FileResponse(
        path=pptx_path,
        filename="FinSight_Executive_Presentation.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@router.get("/pdf")
def download_pdf_report():
    pdf_path = os.path.join(settings.REPORTS_DIR, "FinSight_Executive_Summary.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = build_executive_pdf_report()
    return FileResponse(
        path=pdf_path,
        filename="FinSight_Executive_Summary.pdf",
        media_type="application/pdf"
    )
