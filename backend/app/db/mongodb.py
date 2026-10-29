import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "cyberguard_db")


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        if not MONGODB_URI:
            logger.warning("MONGODB_URI not set. Database features are disabled.")
            return
        # Small pool + short timeouts suit Atlas M0 (500 connection cap) and a single small Render instance.
        self.client = AsyncIOMotorClient(MONGODB_URI, maxPoolSize=10, serverSelectionTimeoutMS=8000)
        self.db = self.client[DB_NAME]
        logger.info("MongoDB client initialised (database '%s')", DB_NAME)

    async def ping(self) -> bool:
        if self.client is None:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    async def close(self):
        if self.client:
            self.client.close()


db = MongoDB()


async def get_db():
    if db.db is None:
        await db.connect()
    return db.db
