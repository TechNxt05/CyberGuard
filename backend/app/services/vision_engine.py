from app.services.llm_provider import get_vision_llm, image_message, parse_json_response

PROMPT = """
Analyze this screenshot for cyber threats.
1. Objects: identify any QR codes, logos, payment buttons, or suspicious popups.
2. OCR: extract all text, especially UPI IDs, phone numbers, URLs and transaction IDs.
3. Classification: classify the screenshot (e.g. Phishing Page, Fake Payment, Support Scam, Safe).
4. Tampering: note visible signs of manipulation (misaligned text, mismatched fonts). This is a visual
   judgement, not forensic proof - say so in the reasoning if you flag it.

Return ONLY a JSON object with this schema:
{
    "objects_detected": ["list of objects"],
    "extracted_text": {"upi_ids": [], "urls": [], "phones": [], "transaction_ids": [], "raw_text": ""},
    "classification": "Phishing Page",
    "tampering_suspected": false,
    "reasoning": "Explanation of findings."
}
"""


class VisionEngine:
    async def analyze_screenshot(self, base64_image: str, mime_type: str = "image/jpeg") -> dict:
        response = await get_vision_llm().ainvoke([image_message(PROMPT, base64_image, mime_type or "image/jpeg")])
        return parse_json_response(response.content)
