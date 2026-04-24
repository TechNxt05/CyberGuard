import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json

class VisionEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model="gemini-1.5-pro",
            temperature=0.1
        ) if self.api_key else None

    async def analyze_screenshot(self, base64_image: str) -> dict:
        """Simulates YOLO/SAM pipeline using VLM for lightweight deployability."""
        if not self.model:
            return {"error": "Vision API key missing. Cannot analyze image."}
            
        prompt = """
        Analyze this image for cyber threats as a highly capable Vision Intelligence Engine.
        Perform the following tasks:
        1. Object Detection: Identify any QR codes, logos, payment buttons, or suspicious popups.
        2. OCR: Extract all text, specifically looking for UPI IDs, phone numbers, URLs, and transaction IDs.
        3. Classification: Classify the screenshot type (e.g., Phishing Page, Fake Payment, Support Scam, Safe).
        4. Tampering: Detect any signs of digital manipulation (misaligned text, mismatched fonts, compression artifacts).
        
        Return the result as a strict JSON object with the following schema:
        {
            "objects_detected": ["list of objects"],
            "extracted_text": {
                "upi_ids": [],
                "urls": [],
                "phones": [],
                "transaction_ids": [],
                "raw_text": ""
            },
            "classification": "Phishing Page",
            "tampering_detected": false,
            "tampering_confidence": 0.0,
            "reasoning": "Explanation of findings."
        }
        """
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        )
        
        try:
            response = await self.model.ainvoke([message])
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}

class FraudEntityExtractor:
    def __init__(self):
        from backend.app.services.llm_provider import get_llm
        self.llm = get_llm()
        
    async def extract_entities(self, text: str) -> dict:
        prompt = f"""
        Extract the following entities from the text if present:
        UPI IDs, Bank Accounts, IFSC, URLs, IP addresses, Crypto Wallets, Transaction IDs, Phone numbers, Names.
        
        Text: "{text}"
        
        Return as strict JSON:
        {{
            "upi_ids": [],
            "bank_accounts": [],
            "ifsc": [],
            "urls": [],
            "crypto_wallets": [],
            "transaction_ids": [],
            "phones": [],
            "names": []
        }}
        """
        try:
            from langchain_core.messages import HumanMessage
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except:
            return {}
