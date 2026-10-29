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


# ---------- Evidence package for 1930 / cybercrime.gov.in ----------

class ComplaintDetails(BaseModel):
    """Fields the National Cybercrime Reporting Portal's financial-fraud complaint asks for."""
    incident_datetime: str = Field("", description="When it happened, as stated by the victim (empty if unknown)")
    category: str = Field("", description="e.g. UPI fraud, phishing, sextortion, investment fraud")
    platform: str = Field("", description="Where it happened, e.g. WhatsApp, phone call, SMS, website")
    amount_lost: str = Field("", description="Total amount lost with currency, empty if none or unknown")
    payment_mode: str = Field("", description="UPI / card / net banking / crypto / cash, empty if unknown")
    transaction_ids: list[str] = Field(default_factory=list)
    victim_bank_or_wallet: str = Field("", description="Victim's bank/wallet the money left from, empty if unknown")
    suspect_details: list[str] = Field(default_factory=list, description="Names, aliases or profiles used by the suspect")
    narrative: str = Field("", description="Factual, chronological description under 200 words, first person, no speculation")


async def _complaint_details(case: dict, history: list[dict]) -> ComplaintDetails:
    from app.services.llm_provider import astructured_call

    user_text = "\n".join(m["content"] for m in history if m.get("sender") == "user")
    attachments = "\n".join(m["attachment"]["extracted_text"] for m in history if m.get("attachment", {}).get("extracted_text"))
    try:
        return await astructured_call(
            "You prepare cybercrime complaint details for an Indian victim. Use ONLY facts stated in the conversation "
            "or screenshot text; leave a field empty rather than guessing.",
            f"Case summary: {case.get('incident_summary', '')}\nAttack type: {case.get('attack_type', '')}\n\n"
            f"Victim's messages:\n{user_text[:6000]}\n\nScreenshot text:\n{attachments[:4000]}",
            ComplaintDetails,
            temperature=0.1,
        )
    except Exception:
        return ComplaintDetails(category=case.get("attack_type") or "", narrative=case.get("incident_summary") or "")


@router.post("/evidence-package", dependencies=[Depends(read_only)])
async def evidence_package(request: ReportRequest, user_id: str = Depends(get_current_user)):
    """One-page brief with everything the 1930 helpline and cybercrime.gov.in complaint form ask for."""
    from app.services.entity_extraction import extract_entities

    case = await get_case(user_id, request.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    history = await get_case_history(request.case_id, user_id, limit=200)
    details = await _complaint_details(case, history)

    # Indicators come from deterministic extraction, never from the LLM.
    corpus = "\n".join([m["content"] for m in history if m.get("sender") == "user"]
                       + [m["attachment"].get("extracted_text", "") for m in history if m.get("attachment")])
    indicators = extract_entities(corpus)
    attachments = [m for m in history if m.get("attachment")]

    pdf = _ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Cybercrime Complaint - Evidence Package", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.para(f"Prepared {datetime.utcnow():%Y-%m-%d %H:%M} UTC with CyberGuardAI. Verify every detail before submitting.")

    pdf.heading("Report it now")
    pdf.para("1. Call 1930 (National Cybercrime Helpline) immediately - the earlier you report, the better the chance of freezing the money.")
    pdf.para("2. File a complaint at https://cybercrime.gov.in -> 'Report Cyber Crime' -> Financial Fraud, and note the acknowledgement number.")
    pdf.para("3. Inform your bank / wallet and ask them to block the transaction and raise a dispute.")

    pdf.heading("Complaint details")
    for label, value in [
        ("Date & time of incident", details.incident_datetime),
        ("Category", details.category),
        ("Platform / medium", details.platform),
        ("Amount lost", details.amount_lost),
        ("Payment mode", details.payment_mode),
        ("Your bank / wallet", details.victim_bank_or_wallet),
        ("Transaction IDs / UTR", ", ".join(details.transaction_ids)),
        ("Suspect name / profile", ", ".join(details.suspect_details)),
    ]:
        pdf.para(f"{label}: {value or '[fill in]'}")

    pdf.heading("Suspect identifiers (extracted automatically)")
    labels = {"upi_id": "UPI IDs", "phone_number": "Phone numbers", "url": "Websites / links", "email": "Emails", "wallet_address": "Crypto wallets"}
    for key, label in labels.items():
        pdf.para(f"{label}: {', '.join(indicators.get(key, [])) or 'none found'}")

    pdf.heading("Incident description (copy into the complaint)")
    pdf.para(details.narrative or case.get("incident_summary") or "[describe what happened, in order]")

    pdf.heading("Evidence files")
    if attachments:
        pdf.para("Attach these original screenshots to your complaint. The SHA-256 fingerprint proves each file is unchanged:")
        for i, m in enumerate(attachments, 1):
            a = m["attachment"]
            ts = m.get("timestamp")
            stamp = ts.strftime("%Y-%m-%d %H:%M") if isinstance(ts, datetime) else ""
            pdf.para(f"{i}. Uploaded {stamp} UTC, {a.get('size_bytes', 0)} bytes, SHA-256 {a.get('sha256', '')}")
    else:
        pdf.para("No screenshots were uploaded to this case. Keep the original screenshots, bank statement and chat exports ready.")

    pdf.heading("Keep ready")
    for item in ["Bank statement showing the debit(s)", "Screenshots of chats, SMS, call logs and payment confirmations",
                 "ID proof (Aadhaar / PAN)", "Any links, app names or profiles used by the fraudster"]:
        pdf.para(f"- {item}")

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="evidence_package_{request.case_id}.pdf"'},
    )
