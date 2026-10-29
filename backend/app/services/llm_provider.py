import json
import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger(__name__)

# Model names live in env vars so a provider deprecation is a config change, not a code change.
# Check https://ai.google.dev/gemini-api/docs/models and https://console.groq.com/docs/models for current names.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# "-latest" aliases follow Google's current model, so they survive model retirements.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", GEMINI_MODEL)
GROQ_TRANSCRIBE_MODEL = os.getenv("GROQ_TRANSCRIBE_MODEL", "whisper-large-v3-turbo")
# A hung provider call must not hold a request (and the single Render worker's thread) forever.
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))


class LLMUnavailableError(RuntimeError):
    """Raised when no LLM provider is configured."""


def _groq(temperature: float):
    from langchain_groq import ChatGroq
    return ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model=GROQ_MODEL, temperature=temperature, max_retries=1, timeout=LLM_TIMEOUT_SECONDS)


def _gemini(temperature: float, model: str = GEMINI_MODEL):
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(google_api_key=os.getenv("GEMINI_API_KEY"), model=model, temperature=temperature, max_retries=1, timeout=LLM_TIMEOUT_SECONDS)


@lru_cache(maxsize=None)
def get_llm(temperature: float = 0.3) -> BaseChatModel:
    """
    Returns a chat model with automatic fallback: Groq (primary) -> Gemini (backup).
    Both have free tiers. Clients are created lazily and cached per temperature.
    """
    models = []
    if os.getenv("GROQ_API_KEY"):
        models.append(_groq(temperature))
    if os.getenv("GEMINI_API_KEY"):
        models.append(_gemini(temperature))

    if not models:
        raise LLMUnavailableError("No LLM API key configured. Set GROQ_API_KEY and/or GEMINI_API_KEY.")
    if len(models) == 1:
        return models[0]
    return models[0].with_fallbacks(models[1:])


@lru_cache(maxsize=None)
def get_vision_llm() -> BaseChatModel:
    """Gemini is the only free provider here that accepts images."""
    if not os.getenv("GEMINI_API_KEY"):
        raise LLMUnavailableError("Image analysis requires GEMINI_API_KEY.")
    return _gemini(0.1, model=GEMINI_VISION_MODEL)


def image_message(prompt: str, image_base64: str, mime_type: str = "image/jpeg"):
    from langchain_core.messages import HumanMessage
    return HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
    ])


def parse_json_response(content) -> dict:
    """Parses an LLM response that should be JSON, tolerating ```json fences and surrounding prose."""
    if isinstance(content, list):  # some providers return content blocks
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    text = str(content).strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def response_text(content) -> str:
    if isinstance(content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return str(content)


def _structured_messages(system: str, user: str, model_cls: type[BaseModel]):
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.output_parsers import PydanticOutputParser

    instructions = PydanticOutputParser(pydantic_object=model_cls).get_format_instructions()
    return [SystemMessage(content=f"{system}\n\n{instructions}\nReturn ONLY the JSON object."), HumanMessage(content=user)]


def structured_call(system: str, user: str, model_cls: type[BaseModel], temperature: float = 0.2) -> BaseModel:
    """
    One LLM call that must return JSON matching `model_cls`. Raises on failure so callers
    decide their own (honest) fallback instead of silently inventing data.
    """
    response = get_llm(temperature).invoke(_structured_messages(system, user, model_cls))
    return model_cls(**parse_json_response(response.content))


async def astructured_call(system: str, user: str, model_cls: type[BaseModel], temperature: float = 0.2) -> BaseModel:
    response = await get_llm(temperature).ainvoke(_structured_messages(system, user, model_cls))
    return model_cls(**parse_json_response(response.content))


def text_call(system: str, user: str, temperature: float = 0.3) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    response = get_llm(temperature).invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return response_text(response.content)


async def atext_call(system: str, user: str, temperature: float = 0.3) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    response = await get_llm(temperature).ainvoke([SystemMessage(content=system), HumanMessage(content=user)])
    return response_text(response.content)
