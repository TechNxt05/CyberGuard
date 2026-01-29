import os
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import praw
import tweepy

# Initialize LLM for summarization
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def search_incident_info(query: str, context: Dict[str, Any] = None) -> str:
    """
    Orchestrates a multi-source search (Web, Reddit, Twitter) and returns a synthesized summary.
    """
    print(f"--- RESEARCH: Starting search for '{query}' ---")
    
    # 1. General Web Search (DuckDuckGo)
    web_results = perform_web_search(query)
    
    # 2. Reddit Search (API -> Fallback to Site Search)
    reddit_results = perform_reddit_search(query)
    
    # 3. Twitter Search (API -> Fallback to Site Search)
    twitter_results = perform_twitter_search(query)
    
    # 4. Synthesize Findings
    all_findings = f"""
    WEB SEARCH FINDINGS:
    {web_results}
    
    REDDIT DISCUSSIONS:
    {reddit_results}
    
    TWITTER/X UPDATES:
    {twitter_results}
    """
    
    # 5. Summarize with LLM
    try:
        summary_prompt = f"""
        You are a Cyber Security Researcher. Synthesize the following raw search data about '{query}' into a concise, actionable research briefing.
        Focus on:
        1. Latest containment steps (how to stop the attack).
        2. Verified recovery forms or links.
        3. Common pitfalls or new variants of this scam.
        
        RAW DATA:
        {all_findings[:8000]}
        
        RESEARCH BRIEFING:
        """
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        print(f"--- RESEARCH: Synthesis failed: {e} ---")
        return all_findings[:2000] # Return raw top results as fallback

def perform_web_search(query: str) -> str:
    """
    Uses DuckDuckGo to find general remediation steps.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # Search for 'solution', 'help', 'support' related to the query
            search_query = f"{query} solution fix help support"
            for r in ddgs.text(search_query, max_results=4):
                results.append(f"- {r['title']}: {r['body']} ({r['href']})")
        return "\n".join(results) if results else "No specific web results found."
    except Exception as e:
        print(f"--- RESEARCH: Web search failed: {e} ---")
        return "Web search unavailable."

def perform_reddit_search(query: str) -> str:
    """
    Tries PRAW API, falls back to DDG 'site:reddit.com'.
    """
    try:
        # Check for credentials
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "CyberGuardAI/1.0")
        
        if client_id and client_secret:
            print("--- RESEARCH: Using Reddit API ---")
            reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
            
            results = []
            for submission in reddit.subreddit("all").search(query, limit=3):
                results.append(f"- [Reddit] {submission.title}: {submission.selftext[:200]}... ({submission.url})")
            return "\n".join(results)
        else:
            raise ValueError("No credentials")
            
    except Exception as e:
        print(f"--- RESEARCH: Reddit API unavailable ({e}). Falling back to Site Search. ---")
        return perform_site_fallback(query, "reddit.com")

def perform_twitter_search(query: str) -> str:
    """
    Tries Tweepy API, falls back to DDG 'site:twitter.com'.
    """
    try:
        # Check for credentials
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if bearer_token:
            print("--- RESEARCH: Using Twitter API ---")
            client = tweepy.Client(bearer_token=bearer_token)
            # Simple search (requires Basic/Pro usually, might fail on Free)
            tweets = client.search_recent_tweets(query=query, max_results=10)
            
            results = []
            if tweets.data:
                for tweet in tweets.data:
                    results.append(f"- [Twitter] {tweet.text}")
            return "\n".join(results)
        else:
            raise ValueError("No credentials")
            
    except Exception as e:
        print(f"--- RESEARCH: Twitter API unavailable ({e}). Falling back to Site Search. ---")
        return perform_site_fallback(query, "twitter.com")

def perform_site_fallback(query: str, domain: str) -> str:
    """
    Uses DuckDuckGo to search a specific domain.
    """
    try:
        results = []
        with DDGS() as ddgs:
            search_query = f"site:{domain} {query}"
            for r in ddgs.text(search_query, max_results=3):
                results.append(f"- [{domain}] {r['title']}: {r['body']} ({r['href']})")
        return "\n".join(results) if results else f"No results found on {domain}."
    except Exception as e:
        return f"Fallback search for {domain} failed."
