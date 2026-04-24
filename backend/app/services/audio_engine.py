import os
from backend.app.services.llm_provider import get_llm
from langchain_core.messages import HumanMessage

class AudioEngine:
    def __init__(self):
        self.llm = get_llm()

    async def analyze_audio(self, audio_bytes: bytes, filename: str) -> dict:
        """
        Simulates Whisper transcription and Deepfake audio detection.
        In a production environment, this would call OpenAI Whisper API or a local Whisper/ResNet model.
        For deployability without massive GPU overhead, we mock the result based on filename/context for now,
        or we could integrate an external API here.
        """
        # Note: True transcription requires sending the file to an API (like OpenAI's audio/transcriptions).
        # We will mock the transcription and use the LLM to calculate "scam probability" based on typical patterns.
        
        # MOCK IMPLEMENTATION
        transcript = f"Mock transcription of {filename}: 'Hello, this is customer support from your bank. Your account has been blocked. Please share your OTP to unblock it immediately.'"
        
        prompt = f"""
        Analyze this audio transcript for scam patterns and deepfake probability.
        Transcript: "{transcript}"
        
        Identify:
        1. Deepfake probability (0-100) based on unnatural language or known robocall patterns.
        2. Scam Risk Score (0-100).
        3. Suspicious entities (names, numbers).
        
        Return strict JSON:
        {{
            "transcript": "{transcript}",
            "deepfake_probability": 85.5,
            "scam_risk_score": 95.0,
            "suspicious_entities": [],
            "summary": "Reasoning here"
        }}
        """
        
        try:
            import json
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}
