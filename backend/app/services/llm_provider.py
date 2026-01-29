import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    Returns a Chat Model with automatic fallback logic.
    Priority: OpenAI -> Gemini -> Groq.
    
    If a key is missing for a provider, it is skipped.
    If all fail or no keys valid, it raises an error (but users asked to avoid this, 
    so we assume at least one key is provided or use a mock fallback for dev if needed).
    """
    
    models = []
    
    # 1. Groq (Prioritize Groq since Gemini is giving Key errors)
    if os.getenv("GROQ_API_KEY"):
        try:
            groq_llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama-3.3-70b-versatile", 
                temperature=temperature,
                max_retries=2
            )
            models.append(groq_llm)
            print("✅ Groq initialized successfully (llama-3.3-70b-versatile)")
        except Exception as e:
             print(f"Failed to init Groq: {e}")

    # 2. Gemini (Secondary)
    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini_llm = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GEMINI_API_KEY"),
                model="gemini-1.5-flash",
                temperature=temperature,
                convert_system_message_to_human=True, 
                max_retries=2
            )
            models.append(gemini_llm)
            print("✅ Gemini initialized successfully")
        except Exception as e:
             print(f"Failed to init Gemini: {e}")

    # 3. OpenAI (Backup)
    # Only try if key looks real (not dummy)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and len(openai_key) > 10 and not openai_key.startswith("aaaaa"):
        try:
            openai_llm = ChatOpenAI(
                api_key=openai_key,
                model="gpt-4o-mini", 
                temperature=temperature,
                max_retries=2
            )
            models.append(openai_llm)
        except Exception as e:
            print(f"Failed to init OpenAI: {e}")

    if not models:
        # Emergency Mock for Dev if no keys at all (prevents hard crash on init, fails at runtime)
        print("WARNING: No LLM API Keys found! Using OpenAI mock wrapper that will likely fail on invoke.")
        return ChatOpenAI(api_key="mock", model="gpt-4o-mini")

    # If only one model, return it
    if len(models) == 1:
        return models[0]

    # Chain fallbacks: primary.with_fallbacks([backup1, backup2])
    primary = models[0]
    backups = models[1:]
    return primary.with_fallbacks(backups)
