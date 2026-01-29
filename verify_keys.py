from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv("backend/.env")

gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

print(f"Gemini Key Loaded: {'Yes' if gemini_key else 'No'}")
if gemini_key:
    print(f"Gemini Key Length: {len(gemini_key)}")
    print(f"Gemini Key starts/ends with space: {gemini_key.strip() != gemini_key}")
    
print(f"Groq Key Loaded: {'Yes' if groq_key else 'No'}")

# Test Gemini
if gemini_key:
    print("\n--- Testing Gemini ---")
    try:
        # Try latest model
        print("Attempting model: gemini-1.5-flash")
        llm = ChatGoogleGenerativeAI(google_api_key=gemini_key, model="gemini-1.5-flash")
        res = llm.invoke("Hello")
        print(f"✅ gemini-1.5-flash Success: {res.content}")
    except Exception as e:
        print(f"❌ gemini-1.5-flash Failed: {e}")
        
    try:
        # Try legacy model
        print("Attempting model: gemini-pro")
        llm = ChatGoogleGenerativeAI(google_api_key=gemini_key, model="gemini-pro")
        res = llm.invoke("Hello")
        print(f"✅ gemini-pro Success: {res.content}")
    except Exception as e:
        print(f"❌ gemini-pro Failed: {e}")

# Test Groq
if groq_key:
    print("\n--- Testing Groq ---")
    
    models_to_test = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
    
    for model in models_to_test:
        try:
            print(f"Attempting model: {model}")
            llm = ChatGroq(api_key=groq_key, model_name=model)
            res = llm.invoke("Hello")
            print(f"✅ {model} Success: {res.content}")
            break # Stop after first success
        except Exception as e:
            print(f"❌ {model} Failed: {e}")
