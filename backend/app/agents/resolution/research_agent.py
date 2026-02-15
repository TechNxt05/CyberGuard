import os
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
# OpenAI import intentionally wrapped in try/except or handled via standard invoke if package exists, 
# but for now we basically mock or check key.
import praw
import tweepy
import concurrent.futures

# Initialize Summarizer LLM (Default to Groq for speed/cost)
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def search_incident_info(query: str, context: Dict[str, Any] = None) -> str:
    """
    Orchestrates a comprehensive multi-source investigation:
    1. Real-time Web (DuckDuckGo)
    2. News (DuckDuckGo News)
    3. Social Signals (Reddit, Twitter)
    4. AI Consensus (Gemini, Groq, OpenAI - if available)
    
    Returns a synthesized "Master Report".
    """
    print(f"--- RESEARCH: Starting Multi-Source Aggregation for '{query}' ---")
    
    # Execute searches in parallel to reduce latency
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Web & News
        future_web = executor.submit(perform_web_search, query)
        future_news = executor.submit(perform_news_search, query)
        
        # Social
        future_reddit = executor.submit(perform_reddit_search, query)
        future_twitter = executor.submit(perform_twitter_search, query)
        
        # AI Internal Knowledge (Consensus Check)
        future_ai = executor.submit(consult_ai_models, query)
        
        # Gather Results
        web_results = future_web.result()
        news_results = future_news.result()
        reddit_results = future_reddit.result()
        twitter_results = future_twitter.result()
        ai_consensus = future_ai.result()

    # Synthesize Findings
    all_findings = f"""
    === 1. REAL-TIME WEB SEARCH ===
    {web_results}
    
    === 2. NEWS & MEDIA ===
    {news_results}
    
    === 3. SOCIAL MEDIA SIGNALS (REDDIT/X) ===
    REDDIT:
    {reddit_results}
    
    TWITTER/X:
    {twitter_results}
    
    === 4. AI MODEL CONSENSUS (INTERNAL KNOWLEDGE) ===
    {ai_consensus}
    """
    
    # Summarize with LLM
    try:
        summary_prompt = f"""
        You are the CyberGuard "Master Investigator". 
        Your goal is to provide the single BEST, most complete answer to the user by combining all available intelligence sources.
        
        QUERY: "{query}"
        
        INTELLIGENCE SOURCES:
        {all_findings[:12000]} 
        
        INSTRUCTIONS:
        1. **Verdict**: Is this a confirmed scam? (Yes/No/Likely). Cite the most credible source.
        2. **Mechanism**: Explain exactly how it works (combine Web + AI knowledge).
        3. **Immediate Action**: What should the user do NOW? (Use the best advice from all sources).
        4. **Official Channels**: List verified URLs/Emails for reporting (prioritize Official gov/company links found in Web/News).
        5. **Community Intel**: Mention if this is trending or what victims are saying (from Reddit/Twitter).
        
        Format as a clean, markdown report. NO generic fluff.
        """
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        print(f"--- RESEARCH: Synthesis failed: {e} ---")
        return all_findings[:4000] # Fallback to raw data

def perform_web_search(query: str) -> str:
    """DuckDuckGo General Search"""
    try:
        results = []
        with DDGS() as ddgs:
            search_query = f"{query} scam review fraud check"
            for r in ddgs.text(search_query, max_results=5):
                results.append(f"- [WEB] {r['title']}: {r['body']} ({r['href']})")
        return "\n".join(results) if results else "No specific web results."
    except Exception as e:
        return f"Web search error: {e}"

def perform_news_search(query: str) -> str:
    """DuckDuckGo News Search"""
    try:
        results = []
        with DDGS() as ddgs:
            # removing 'scam' to get broader news if query is just entity name, 
            # but usually query includes 'scam' if it's from the detector.
            for r in ddgs.news(query, max_results=5): 
                results.append(f"- [NEWS] {r['title']} ({r['source']}): {r['body']} ({r['url']})")
        return "\n".join(results) if results else "No recent news articles found."
    except Exception as e:
        return f"News search error: {e}"

def perform_reddit_search(query: str) -> str:
    """PRAW -> Fallback to Site Search"""
    try:
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "CyberGuardAI/1.0")
        
        if client_id and client_secret:
            reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
            results = []
            for submission in reddit.subreddit("all").search(query, limit=5):
                results.append(f"- [REDDIT] {submission.title}: {submission.selftext[:200]}... ({submission.url})")
            return "\n".join(results)
        else:
            raise ValueError("No credentials")
    except Exception:
        return perform_site_fallback(query, "reddit.com")

def perform_twitter_search(query: str) -> str:
    """Tweepy -> Fallback to Site Search"""
    try:
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if bearer_token:
            client = tweepy.Client(bearer_token=bearer_token)
            tweets = client.search_recent_tweets(query=query, max_results=10)
            results = []
            if tweets.data:
                for tweet in tweets.data:
                    results.append(f"- [TWITTER] {tweet.text}")
            return "\n".join(results)
        else:
            raise ValueError("No credentials")
    except Exception:
        return perform_site_fallback(query, "twitter.com")

def perform_site_fallback(query: str, domain: str) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(f"site:{domain} {query} scam", max_results=4):
                 results.append(f"- [{domain} Search] {r['title']}: {r['body']} ({r['href']})")
        return "\n".join(results) if results else f"No results on {domain}."
    except Exception:
        return f"Search unavailable for {domain}."

def consult_ai_models(query: str) -> str:
    """
    Asks Gemini and Groq (and OpenAI if avail) for their internal knowledge.
    """
    ai_insights = []
    
    # 1. Google Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GEMINI_API_KEY"),
                model="gemini-1.5-flash", 
                temperature=0
            )
            resp = gemini.invoke(f"Briefly explain the scam mechanism related to: '{query}'. If unknown, say 'Unknown'.")
            ai_insights.append(f"GEMINI KNOWLEDGE:\n{resp.content}")
        except Exception as e:
            ai_insights.append(f"GEMINI ERROR: {e}")
            
    # 2. Groq (Llama-3)
    if os.getenv("GROQ_API_KEY"):
        try:
            # using a different instance or same one, doesn't matter much.
            groq_llm = ChatGroq(
                temperature=0,
                model_name="llama-3.3-70b-versatile", 
                api_key=os.getenv("GROQ_API_KEY")
            )
            resp = groq_llm.invoke(f"What are the key red flags for: '{query}'? Keep it brief.")
            ai_insights.append(f"GROQ (LLAMA-3) KNOWLEDGE:\n{resp.content}")
        except Exception as e:
            ai_insights.append(f"GROQ ERROR: {e}")

    # 3. OpenAI (Optional/Future)
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            openai_llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
            resp = openai_llm.invoke(f"Analyze the threat level of: '{query}'.")
            ai_insights.append(f"OPENAI (GPT-4) KNOWLEDGE:\n{resp.content}")
        except Exception:
            pass # Silent fail if lib not installed or key invalid

    if not ai_insights:
        return "No AI Internal Knowledge available (Keys missing)."
        
    return "\n---\n".join(ai_insights)
