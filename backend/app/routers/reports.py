from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fpdf import FPDF
from pydantic import BaseModel, Field

from app.auth.clerk_auth import get_current_user
from app.services.case_store import get_case, get_case_history, get_tasks
from app.services.rate_limit import read_only

router = APIRouter(prefix="/api/reports", tags=["Reports"])

# The built-in PDF fonts are Latin-1 only; map common characters instead of crashing on them.
_REPLACEMENTS = {"₹": "Rs.", "–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"', "•": "-", "…": "..."}


def _latin1(text) -> str:
    text = str(text or "")
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class ReportRequest(BaseModel):
    case_id: str = Field(..., min_length=1, max_length=100)


class _ReportPDF(FPDF):
    def heading(self, text: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, _latin1(text), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)

    def para(self, text: str):
        self.multi_cell(0, 6, _latin1(text), new_x="LMARGIN", new_y="NEXT")


@router.post("/export-pdf", dependencies=[Depends(read_only)])
async def export_report_pdf(request: ReportRequest, user_id: str = Depends(get_current_user)):
    """PDF summary of a case: incident details, action checklist and conversation log."""
    case = await get_case(user_id, request.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    history = await get_case_history(request.case_id, user_id, limit=200)
    tasks = await get_tasks(request.case_id, user_id)

    pdf = _ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CyberGuard Incident Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.para(f"Case ID: {request.case_id}")
    pdf.para(f"Title: {case.get('title', 'Unknown')}")
    pdf.para(f"Status: {case.get('status', 'Unknown')}")
    pdf.para(f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M} UTC")

    pdf.heading("Incident Summary")
    pdf.para(case.get("incident_summary") or "No summary available.")
    if case.get("attack_type"):
        pdf.para(f"Attack type: {case['attack_type']}")
    if case.get("incident_logic"):
        pdf.para(f"How it works: {case['incident_logic']}")

    if tasks:
        pdf.heading("Action Checklist")
        for i, t in enumerate(tasks, 1):
            mark = "[x]" if t.get("status") == "completed" else "[ ]"
            pdf.para(f"{mark} {i}. {t.get('label', '')}")

    if case.get("prevention_tips"):
        pdf.heading("Prevention Tips")
        for tip in case["prevention_tips"]:
            pdf.para(f"- {tip}")

    if history:
        pdf.heading("Conversation Log")
        for m in history:
            ts = m.get("timestamp")
            stamp = ts.strftime("%Y-%m-%d %H:%M") if isinstance(ts, datetime) else ""
            pdf.para(f"[{stamp}] {str(m.get('sender', '')).upper()}: {m.get('content', '')}")

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="cyberguard_report_{request.case_id}.pdf"'},
    )
