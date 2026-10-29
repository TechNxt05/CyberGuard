"""
Deletes all documents from selected collections.

    python scripts/clear_db.py threat_entities --yes     # reset threat memory only
    python scripts/clear_db.py --all --yes               # everything
"""
import argparse
import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

COLLECTIONS = ["cases", "case_messages", "case_tasks", "case_state", "scam_reports", "threat_entities"]


async def clear(collections: list[str]) -> None:
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(dotenv_path=env_path)
    load_dotenv()  # Fallback to local .env if present
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set.")
    db = AsyncIOMotorClient(uri)[os.getenv("MONGODB_DB_NAME", "cyberguard_db")]
    for name in collections:
        result = await db[name].delete_many({})
        print(f"Deleted {result.deleted_count} documents from '{name}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collections", nargs="*", metavar="collection", help=f"one or more of {COLLECTIONS}")
    parser.add_argument("--all", action="store_true", help="clear every collection")
    parser.add_argument("--yes", action="store_true", help="required: confirm deletion")
    args = parser.parse_args()

    targets = COLLECTIONS if args.all else args.collections
    if not targets:
        parser.error("name at least one collection or pass --all")
    unknown = set(targets) - set(COLLECTIONS)
    if unknown:
        parser.error(f"unknown collection(s): {sorted(unknown)}")
    if not args.yes:
        parser.error(f"this permanently deletes all documents in {targets}; re-run with --yes")
    asyncio.run(clear(targets))
