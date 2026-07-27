import os
import sys
import asyncio
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.db.mongodb import db

async def migrate_flat_ledger_to_kg():
    """
    Migration script to convert flat MongoDB threat_entities ledger records
    into an Entity Relationship Knowledge Graph schema.
    """
    print("--- Starting Migration: Flat Ledger -> Entity Relationship Graph ---")
    await db.connect()
    if db.db is None:
        print("Database connection failed. Aborting migration.")
        return

    collection = db.db["threat_entities"]
    cursor = collection.find({})
    records = await cursor.to_list(1000)
    
    migrated = 0
    for doc in records:
        entity_type = doc.get("entity_type", "unknown")
        normalized = doc.get("entity_value_normalized", doc.get("indicator", ""))
        entity_id = doc.get("entity_id", f"{entity_type}_{normalized}")
        
        updates = {
            "entity_id": entity_id,
            "connected_entities": doc.get("connected_entities", []),
            "attack_campaigns": doc.get("attack_campaigns", [f"Campaign_{doc.get('crime_types', ['GENERAL'])[0].upper()}"]),
            "victim_count": doc.get("victim_count", len(doc.get("case_ids", [1]))),
            "geographic_cluster": doc.get("geographic_cluster", "Mumbai/Delhi/NCR")
        }
        
        await collection.update_one({"_id": doc["_id"]}, {"$set": updates})
        migrated += 1
        
    print(f"--- Migration Completed: Successfully updated {migrated} records to KG schema. ---")
    await db.close()

if __name__ == "__main__":
    asyncio.run(migrate_flat_ledger_to_kg())
