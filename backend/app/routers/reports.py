from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from fpdf import FPDF
from backend.app.auth.clerk_auth import get_current_user
from backend.app.mcp_servers.memory.server import get_case, get_case_history

router = APIRouter(prefix="/api/reports", tags=["Reports"])

class ReportRequest(BaseModel):
    case_id: str

@router.post("/export-pdf")
async def export_report_pdf(request: ReportRequest, user_id: str = Depends(get_current_user)):
    """Generates a PDF summary of the investigation."""
    case = await get_case(user_id, request.case_id)
    if "error" in case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    history = await get_case_history(request.case_id, user_id)
    
    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="CyberGuard Investigation Report", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Case ID: {request.case_id}", ln=True)
    pdf.cell(200, 10, txt=f"Title: {case.get('title', 'Unknown')}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {case.get('status', 'Unknown')}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Incident Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, txt=case.get("incident_summary", "No summary available."))
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Extracted Entities & Timeline", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt="(Detailed logs omitted for brief summary)", ln=True)
    
    # Output to BytesIO
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    buffer = io.BytesIO(pdf_bytes)
    
    headers = {
        'Content-Disposition': f'attachment; filename="cyberguard_report_{request.case_id}.pdf"'
    }
    
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
