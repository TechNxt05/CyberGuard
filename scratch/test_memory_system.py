import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure CyberGuard project folders are in PYTHONPATH
project_root = r"c:\Users\Amritanshu\OneDrive\Desktop\Project - 2\CyberGuard"
sys.path.insert(0, project_root)

# Load env variables from backend/.env file
load_dotenv(os.path.join(project_root, "backend", ".env"))

from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.services.memory_service import ThreatMemoryService

async def main():
    print("Initializing test for Persistent Threat Memory Layer...")
    
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("Error: MONGODB_URI not found in environment!")
        return
        
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_uri)
    db = client["cyberguard_test_db"] # Use a test db to prevent contaminating production data
    
    service = ThreatMemoryService(db)
    
    # Clean up test collection before we start
    print("Clearing test database collection...")
    await db["threat_entities"].drop()
    
    await service.ensure_indexes()
    print("Created database indexes successfully.")
    
    # 1. Store first occurrence
    case_1_id = "test-case-001"
    scam_upi = "scammer.test@ybl"
    phish_url = "http://scam-sbi-update.net"
    
    entities = {
        "upi_id": [scam_upi],
        "url": [phish_url]
    }
    
    print("\n--- TEST 1: Storing first occurrence of threat entities ---")
    res1 = await service.store_entities(entities, case_1_id, "financial_fraud")
    print(f"Result 1: {res1}")
    
    # Verify risk score is 0.3 for occurrence 1
    matches = await service.check_entities(entities)
    print(f"Matches count: {len(matches)}")
    for m in matches:
        print(f"Entity: {m['entity_value']} | Type: {m['entity_type']} | Occurrences: {m['occurrence_count']} | Risk: {m['risk_score']} | Confirmed: {m['is_confirmed_threat']}")
        assert m['occurrence_count'] == 1
        assert abs(m['risk_score'] - 0.3) < 1e-5
        assert m['is_confirmed_threat'] == False
        
    # 2. Store second occurrence of same UPI ID
    case_2_id = "test-case-002"
    entities_2 = {
        "upi_id": [scam_upi]
    }
    
    print("\n--- TEST 2: Storing second occurrence of the same UPI handle ---")
    res2 = await service.store_entities(entities_2, case_2_id, "phishing")
    print(f"Result 2: {res2}")
    
    matches_2 = await service.check_entities(entities)
    for m in matches_2:
        if m['entity_value'] == scam_upi:
            print(f"Entity: {m['entity_value']} | Type: {m['entity_type']} | Occurrences: {m['occurrence_count']} | Risk: {m['risk_score']} | Confirmed: {m['is_confirmed_threat']}")
            assert m['occurrence_count'] == 2
            assert abs(m['risk_score'] - 0.5) < 1e-5
            assert m['is_confirmed_threat'] == False
            
    # 3. Store third occurrence of same UPI ID (should escalate risk and mark as confirmed threat)
    case_3_id = "test-case-003"
    entities_3 = {
        "upi_id": [scam_upi]
    }
    
    print("\n--- TEST 3: Storing third occurrence (Escalation to CONFIRMED THREAT) ---")
    res3 = await service.store_entities(entities_3, case_3_id, "identity_theft")
    print(f"Result 3: {res3}")
    
    matches_3 = await service.check_entities(entities)
    for m in matches_3:
        if m['entity_value'] == scam_upi:
            print(f"Entity: {m['entity_value']} | Type: {m['entity_type']} | Occurrences: {m['occurrence_count']} | Risk: {m['risk_score']} | Confirmed: {m['is_confirmed_threat']}")
            assert m['occurrence_count'] == 3
            assert abs(m['risk_score'] - 0.7) < 1e-5
            assert m['is_confirmed_threat'] == True
            
    # 4. Fetch global stats
    print("\n--- TEST 4: Verifying Global Stats Calculation ---")
    stats = await service.get_threat_stats()
    print(f"Platform Stats: {stats}")
    assert stats["total_tracked_entities"] == 2 # 1 upi_id + 1 url
    assert stats["confirmed_threats"] == 1 # scam_upi is confirmed threat
    assert stats["high_risk_entities"] == 1 # scam_upi has 0.7 risk
    
    # 5. Clean up test database
    print("\nCleaning up test collections...")
    await db["threat_entities"].drop()
    print("SUCCESS: All Persistent Memory Layer tests passed successfully!")
    
if __name__ == "__main__":
    asyncio.run(main())
