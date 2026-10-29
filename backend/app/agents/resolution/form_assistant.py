from app.services.llm_provider import atext_call

SYSTEM = """You are a Legal Drafting Assistant.
Write a clear, professional, concise 'Incident Description' the user can copy and paste into an official complaint form
(FIR, bank dispute, National Cybercrime Reporting Portal).

Include:
- Date/Time (use placeholders like [DATE] if unknown)
- Amount lost (if financial)
- Transaction IDs (if available, otherwise [TRANSACTION ID])
- Suspect details (if any)
- Chronological flow of events

Keep it under 200 words, as some forms have limits. Start directly with the text. No conversational filler."""


async def generate_form_text(dimensions: dict, request: str = "") -> str:
    """Generates copy-paste complaint text from the stored incident dimensions."""
    user = f"""
Incident summary: {dimensions.get("summary", "unknown")}
Asset affected: {dimensions.get("asset_affected", [])}
Attack type: {dimensions.get("attack_type", "unknown")}
Urgency: {dimensions.get("urgency", "unknown")}
Authorities: {dimensions.get("control_authority", [])}
User's request / extra details: {request}
"""
    return await atext_call(SYSTEM, user, temperature=0.3)
