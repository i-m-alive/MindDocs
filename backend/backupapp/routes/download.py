from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from fpdf import FPDF

from app.utils.database import get_db
from app.models.summary import SummaryHistory

router = APIRouter()

@router.get("/download/summary/pdf")
def download_summary_as_pdf(
    summary_id: int = Query(..., description="ID of the summary to download"),
    db: Session = Depends(get_db)
):
    """
    Generate and download a PDF version of the summary based on summary_id.

    Args:
        summary_id (int): ID of the summary history (logged after summarization)
    
    Returns:
        PDF file as StreamingResponse
    """

    # ✅ Step 1: Fetch summary from DB
    summary = db.query(SummaryHistory).filter_by(id=summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found.")

    # ✅ Step 2: Generate PDF in memory
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header Info
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Summary for: {summary.document.name}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Domain: {summary.domain} | Word Ratio: {summary.compression_ratio}", ln=True)
    pdf.cell(0, 10, f"Generated on: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # Summary Text
    pdf.set_font("Arial", '', 12)
    for line in summary.summary_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    # ✅ Step 3: Output to BytesIO
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    # ✅ Step 4: Return as downloadable response
    filename = f"summary_{summary_id}.pdf"
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
