from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

# An indicator becomes a "confirmed threat" only when this many *different signed-in users* reported it,
# so a single caller can't brand an innocent phone number or UPI ID as malicious by repeating it.
CONFIRMATION_THRESHOLD = 3
# Indicators nobody has reported for a year are dropped automatically (MongoDB TTL index on last_seen).
RETENTION_DAYS = 365


def _iso(value) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value)


class ThreatMemoryService:
    """Persistent memory of fraud indicators (UPI IDs, phones, URLs...) across investigations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["threat_entities"]

    @staticmethod
    def _normalize(value: str) -> str:
        return value.lower().strip()

    @staticmethod
    def _compute_risk_score(reporter_count: int) -> float:
        """Risk grows with independent reports: 1 -> 0.3, 2 -> 0.5, 3 -> 0.7, 4 -> 0.85, then slowly to 0.95."""
        scores = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.85}
        if reporter_count <= 0:
            return 0.0
        return scores.get(reporter_count, min(0.95, 0.85 + (reporter_count - 4) * 0.02))

    async def ensure_indexes(self):
        await self.collection.create_index([("entity_type", 1), ("entity_value_normalized", 1)], unique=True)
        await self.collection.create_index([("occurrence_count", 1), ("last_seen", -1)])
        await self.collection.create_index("risk_score")
        await self.collection.create_index("last_seen", expireAfterSeconds=RETENTION_DAYS * 24 * 3600)

    async def store_entities(self, entities: dict, case_id: str, crime_type: str, reporter_id: str) -> dict:
        """Upserts every indicator from one investigation. Returns counts of new vs updated entities."""
        all_ids = [
            f"{etype}_{self._normalize(str(v))}"
            for etype, values in entities.items() for v in (values or []) if v and str(v).strip()
        ]
        new_count = updated_count = 0
        now = datetime.utcnow()

        for entity_type, values in entities.items():
            for value in values or []:
                if not value or not str(value).strip():
                    continue
                normalized = self._normalize(str(value))
                entity_id = f"{entity_type}_{normalized}"
                doc = await self.collection.find_one_and_update(
                    {"entity_type": entity_type, "entity_value_normalized": normalized},
                    {
                        "$setOnInsert": {"entity_id": entity_id, "entity_value": str(value), "first_seen": now},
                        "$set": {"last_seen": now},
                        "$inc": {"occurrence_count": 1},
                        "$addToSet": {
                            "case_ids": case_id,
                            "crime_types": crime_type,
                            "reporter_ids": reporter_id,
                            "connected_entity_ids": {"$each": [i for i in all_ids if i != entity_id]},
                        },
                    },
                    upsert=True,
                    return_document=ReturnDocument.AFTER,
                )
                reporters = len(doc.get("reporter_ids", []))
                await self.collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {
                        "risk_score": self._compute_risk_score(reporters),
                        "is_confirmed_threat": reporters >= CONFIRMATION_THRESHOLD,
                        "victim_count": reporters,
                    }},
                )
                if doc["occurrence_count"] == 1:
                    new_count += 1
                else:
                    updated_count += 1

        return {"new_entities": new_count, "updated_entities": updated_count}

    async def _recompute(self, query: dict) -> None:
        """Re-derives risk after reporters/cases are removed; deletes indicators nobody reports any more."""
        async for doc in self.collection.find(query):
            reporters = len(doc.get("reporter_ids", []))
            if reporters == 0:
                await self.collection.delete_one({"_id": doc["_id"]})
                continue
            await self.collection.update_one({"_id": doc["_id"]}, {"$set": {
                "risk_score": self._compute_risk_score(reporters),
                "is_confirmed_threat": reporters >= CONFIRMATION_THRESHOLD,
                "victim_count": reporters,
            }})

    async def forget_reporter(self, reporter_id: str) -> None:
        """Removes a user's contributions (used when they delete their data)."""
        affected = [d["_id"] async for d in self.collection.find({"reporter_ids": reporter_id}, {"_id": 1})]
        await self.collection.update_many({"_id": {"$in": affected}}, {"$pull": {"reporter_ids": reporter_id}})
        await self._recompute({"_id": {"$in": affected}})

    async def forget_case(self, case_id: str) -> None:
        await self.collection.update_many({"case_ids": case_id}, {"$pull": {"case_ids": case_id}})

    async def check_entities(self, entities: dict) -> list[dict]:
        """Returns known indicators among `entities`, highest risk first."""
        matches = []
        for entity_type, values in entities.items():
            for value in values or []:
                if not value:
                    continue
                existing = await self.collection.find_one(
                    {"entity_type": entity_type, "entity_value_normalized": self._normalize(str(value))}
                )
                if existing:
                    matches.append({
                        "entity_type": entity_type,
                        "entity_value": str(value),
                        "occurrence_count": existing.get("occurrence_count", 1),
                        "first_seen": _iso(existing.get("first_seen")),
                        "last_seen": _iso(existing.get("last_seen")),
                        "crime_types": existing.get("crime_types", []),
                        "risk_score": existing.get("risk_score", 0.0),
                        "is_confirmed_threat": existing.get("is_confirmed_threat", False),
                        "case_count": len(existing.get("case_ids", [])),
                    })
        return sorted(matches, key=lambda x: x["risk_score"], reverse=True)

    async def get_threat_stats(self) -> dict:
        total = await self.collection.count_documents({})
        confirmed = await self.collection.count_documents({"is_confirmed_threat": True})
        high_risk = await self.collection.count_documents({"risk_score": {"$gte": 0.7}})
        pipeline = [{"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        breakdown = await self.collection.aggregate(pipeline).to_list(10)
        return {
            "total_tracked_entities": total,
            "confirmed_threats": confirmed,
            "high_risk_entities": high_risk,
            "type_breakdown": [{"type": item["_id"], "count": item["count"]} for item in breakdown],
        }

    async def get_recent_threats(self, limit: int = 20) -> list[dict]:
        """Indicators seen in 2+ investigations, most recently seen first."""
        cursor = self.collection.find({"occurrence_count": {"$gte": 2}}, sort=[("last_seen", -1)], limit=limit)
        return [
            {
                "entity_type": r["entity_type"],
                "entity_value": r["entity_value"],
                "occurrence_count": r.get("occurrence_count", 1),
                "last_seen": _iso(r.get("last_seen")),
                "crime_types": r.get("crime_types", []),
                "risk_score": r.get("risk_score", 0.0),
                "is_confirmed_threat": r.get("is_confirmed_threat", False),
            }
            for r in await cursor.to_list(limit)
        ]
