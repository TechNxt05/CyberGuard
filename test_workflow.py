import os
import sys

# Ensure backend module is found
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from backend.app.workflows.scamshield_graph import scamshield_app
from backend.app.workflows.cyber_resolve_graph import cyber_resolve_app
from backend.app.schemas.common import AnalysisRequest
from backend.app.schemas.resolution import IncidentRequest
from backend.app.agents.resolution.state_agent import get_case_state
from backend.app.agents.resolution.assistants import resolve_doubt
from dotenv import load_dotenv
import os

# Explicitly load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def test_pipeline():
    print("Testing CyberGuardAI One Pipeline...")
    
    # --- Test 1: ScamShield ---
    print("\n--- TEST 1: ScamShield ---")
    req = AnalysisRequest(
        message="Urgent! Your electricity will be cut tonight at 9PM. Call 9876543210 immediately to pay bill.",
        source="sms"
    )
    
    initial_state_scam = {
        "request": req,
        "user_profile": None, 
        "scout_report": None, 
        "explanation": None, 
        "action_plan": None, 
        "final_output": None
    }
    
    try:
        result = scamshield_app.invoke(initial_state_scam)
        final = result["final_output"]
        print(f"Verdict: {final.scout_report.verdict}")
    except Exception as e:
        print(f"ScamShield Error: {e}")

    # --- Test 2: CyberResolve & Interactive ---
    print("\n--- TEST 2: CyberResolve & Interactive ---")
    incident_req = IncidentRequest(
        description="Someone hacked my Instagram account and is messaging my friends asking for money.",
        user_context={"country": "India"}
    )
    
    initial_state_resolve = {"request": incident_req, "case_state": None, "current_guide": None}
    
    try:
        result_res = cyber_resolve_app.invoke(initial_state_resolve)
        case = result_res["case_state"]
        
        print(f"Incident ID: {case.incident_id}")
        print(f"Attack Type: {case.dimensions.attack_type}")
        print(f"Strategy: {len(case.strategy.lifecycle_plan)} steps generated.")
        print(f"Authorities Identified: {len(case.authorities)}")
        print(f"Initial Guide: {result_res.get('current_guide')}")
        
        # Simulate /case/doubt endpoint
        print("\n--- Testing Doubt Resolution (Interactive) ---")
        saved_case = get_case_state(case.incident_id)
        if saved_case:
            question = "Is it safe to pay the hacker if they promise to give it back?"
            plan_summary = f"Attack: {saved_case.dimensions.attack_type}. Status: {saved_case.status}."
            answer = resolve_doubt(question, plan_summary)
            print(f"User Question: {question}")
            print(f"Agent Answer: {answer}")
        else:
             print("Error: Case state persistence failed.")
            
    except Exception as e:
        print(f"CyberResolve Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
