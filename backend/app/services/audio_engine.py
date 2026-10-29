import os

from pydantic import BaseModel, Field

from app.services.llm_provider import GROQ_TRANSCRIBE_MODEL, LLMUnavailableError, astructured_call


class AudioAssessment(BaseModel):
    scam_risk_score: int = Field(..., ge=0, le=100)
    suspicious_entities: list[str] = Field(default_factory=list)
    summary: str


class AudioEngine:
    """
    Transcribes call recordings with Groq's hosted Whisper (free tier) and assesses the transcript.
    It does NOT detect voice deepfakes - that needs a dedicated acoustic model, not an LLM.
    """

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        if not os.getenv("GROQ_API_KEY"):
            raise LLMUnavailableError("Audio transcription requires GROQ_API_KEY.")
        from groq import AsyncGroq

        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        result = await client.audio.transcriptions.create(file=(filename, audio_bytes), model=GROQ_TRANSCRIBE_MODEL)
        return result.text

    async def analyze_audio(self, audio_bytes: bytes, filename: str) -> dict:
        transcript = await self.transcribe(audio_bytes, filename)
        assessment = await astructured_call(
            "You are a scam-call analyst. Assess this call transcript for scam patterns (urgency, impersonation, OTP/PIN "
            "requests, payment pressure). scam_risk_score is 0-100. List suspicious names, numbers, UPI IDs or URLs.",
            f'Transcript: "{transcript}"',
            AudioAssessment,
            temperature=0.2,
        )
        return {"transcript": transcript, **assessment.model_dump()}
