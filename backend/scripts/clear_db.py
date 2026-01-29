import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def clear_database():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("Error: MONGODB_URI not found in environment.")
        return

    client = AsyncIOMotorClient(uri)
    db = client.get_default_database()
    
    collections = ["cases", "case_tasks", "case_states", "messages"]
    
    print("--- Clearing Database ---")
    for col_name in collections:
        result = await db[col_name].delete_many({})
        print(f"Deleted {result.deleted_count} documents from '{col_name}'")
        
    print("--- Database Cleared Successfully ---")

if __name__ == "__main__":
    asyncio.run(clear_database())
