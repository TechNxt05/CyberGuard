import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "cyberguard_db"

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        if not MONGODB_URI:
            print("Warning: MONGODB_URI not set. Database features will fail.")
            return
        
        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        print("Connected to MongoDB Atlas")

    async def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

db = MongoDB()

async def get_db():
    if db.db is None:
        await db.connect()
    return db.db
