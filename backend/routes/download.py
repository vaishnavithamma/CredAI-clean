from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from backend.routes.risk import latest_result
# ✅ THIS LINE IS VERY IMPORTANT
router = APIRouter()

@router.get("/download-report")
def download_report():
    file_path = "loan_report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("Loan Report", styles["Title"]))
    status = latest_result.get("status", "No Data")
    score = latest_result.get("risk_score", "N/A")

    content.append(Paragraph(f"Status: {status}", styles["Normal"]))
    content.append(Paragraph(f"Risk Score: {score}", styles["Normal"]))

    doc.build(content)

    return FileResponse(file_path, media_type="application/pdf", filename="loan_report.pdf")