from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import re

class ThreatMemoryService:
    """
    Persistent memory layer for threat entities.
    Stores and retrieves entity intelligence across investigation sessions.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["threat_entities"]

    def _normalize(self, value: str) -> str:
        """Normalize entity value for deduplication."""
        return value.lower().strip()

    def _compute_risk_score(self, occurrence_count: int) -> float:
        """Risk score increases with occurrence count, caps at 1.0."""
        # 1 occurrence = 0.3, 3 = 0.7, 5+ = 0.95
        if occurrence_count == 1:
            return 0.3
        elif occurrence_count == 2:
            return 0.5
        elif occurrence_count == 3:
            return 0.7
        elif occurrence_count == 4:
            return 0.85
        else:
            return min(0.95, 0.85 + (occurrence_count - 4) * 0.02)

    async def ensure_indexes(self):
        """Create indexes for threat_entities."""
        await self.collection.create_index("entity_value_normalized")
        await self.collection.create_index("entity_type")
        # Compound index for fast deduplication checks
        await self.collection.create_index([("entity_type", 1), ("entity_value_normalized", 1)], unique=True)

    async def store_entities(
        self,
        entities: dict,  # {entity_type: [values]}
        case_id: str,
        crime_type: str
    ) -> dict:
        """
        Store extracted entities from an investigation.
        Returns count of new vs updated entities.
        """
        new_count = 0
        updated_count = 0

        for entity_type, values in entities.items():
            if not values:
                continue
            for value in values:
                if not value or not str(value).strip():
                    continue

                normalized = self._normalize(str(value))
                entity_id = f"{entity_type}_{normalized}"
                now = datetime.utcnow()

                # Build co-occurring entity connections for this investigation session
                connected = []
                for o_type, o_vals in entities.items():
                    for o_val in o_vals:
                        if not o_val: continue
                        o_norm = self._normalize(str(o_val))
                        o_id = f"{o_type}_{o_norm}"
                        if o_id != entity_id:
                            connected.append({
                                "entity_id": o_id,
                                "relationship": "used_in_same_case",
                                "strength": 0.9
                            })

                # Check if entity already exists
                existing = await self.collection.find_one({
                    "entity_type": entity_type,
                    "entity_value_normalized": normalized
                })

                if existing:
                    # Update existing entity in KG
                    new_count_val = existing.get("occurrence_count", 1) + 1
                    current_cases = existing.get("case_ids", [])
                    if case_id not in current_cases:
                        current_cases.append(case_id)
                        
                    await self.collection.update_one(
                        {"_id": existing["_id"]},
                        {
                            "$set": {
                                "entity_id": entity_id,
                                "last_seen": now,
                                "occurrence_count": new_count_val,
                                "risk_score": self._compute_risk_score(new_count_val),
                                "is_confirmed_threat": new_count_val >= 3,
                                "victim_count": len(current_cases),
                                "geographic_cluster": existing.get("geographic_cluster", "Mumbai/NCR")
                            },
                            "$addToSet": {
                                "case_ids": case_id,
                                "crime_types": crime_type,
                                "connected_entities": {"$each": connected},
                                "attack_campaigns": f"Campaign_{crime_type.upper()}"
                            }
                        }
                    )
                    updated_count += 1
                else:
                    # Insert new KG entity
                    await self.collection.insert_one({
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "entity_value": str(value),
                        "entity_value_normalized": normalized,
                        "first_seen": now,
                        "last_seen": now,
                        "occurrence_count": 1,
                        "case_ids": [case_id],
                        "crime_types": [crime_type],
                        "risk_score": self._compute_risk_score(1),
                        "is_confirmed_threat": False,
                        "connected_entities": connected,
                        "attack_campaigns": [f"Campaign_{crime_type.upper()}"],
                        "victim_count": 1,
                        "geographic_cluster": "Mumbai/NCR",
                        "metadata": {}
                    })
                    new_count += 1

        return {"new_entities": new_count, "updated_entities": updated_count}

    async def check_entities(
        self,
        entities: dict  # {entity_type: [values]}
    ) -> list[dict]:
        """
        Check if any provided entities are known threats.
        Returns list of matches with their history.
        Call this BEFORE running the full investigation pipeline
        so the orchestrator knows about repeat offenders upfront.
        """
        matches = []

        for entity_type, values in entities.items():
            if not values:
                continue
            for value in values:
                if not value:
                    continue

                normalized = self._normalize(str(value))
                existing = await self.collection.find_one({
                    "entity_type": entity_type,
                    "entity_value_normalized": normalized
                })

                if existing:
                    matches.append({
                        "entity_type": entity_type,
                        "entity_value": str(value),
                        "occurrence_count": existing["occurrence_count"],
                        "first_seen": existing["first_seen"].isoformat() if isinstance(existing["first_seen"], datetime) else str(existing["first_seen"]),
                        "last_seen": existing["last_seen"].isoformat() if isinstance(existing["last_seen"], datetime) else str(existing["last_seen"]),
                        "crime_types": existing["crime_types"],
                        "risk_score": existing["risk_score"],
                        "is_confirmed_threat": existing["is_confirmed_threat"],
                        "case_count": len(existing["case_ids"])
                    })

        return sorted(matches, key=lambda x: x["risk_score"], reverse=True)

    async def get_threat_stats(self) -> dict:
        """Dashboard stats for the memory layer."""
        total = await self.collection.count_documents({})
        confirmed = await self.collection.count_documents(
            {"is_confirmed_threat": True}
        )
        high_risk = await self.collection.count_documents(
            {"risk_score": {"$gte": 0.7}}
        )

        # Top entity types
        pipeline = [
            {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_breakdown = await self.collection.aggregate(pipeline).to_list(10)

        # Map type_breakdown properly so it's JSON serializable
        clean_breakdown = [{"type": item["_id"], "count": item["count"]} for item in type_breakdown]

        return {
            "total_tracked_entities": total,
            "confirmed_threats": confirmed,
            "high_risk_entities": high_risk,
            "type_breakdown": clean_breakdown
        }

    async def get_recent_threats(self, limit: int = 20) -> list[dict]:
        """Get recently seen threat entities for the intelligence feed."""
        cursor = self.collection.find(
            {"occurrence_count": {"$gte": 2}},
            sort=[("last_seen", -1)],
            limit=limit
        )
        results = await cursor.to_list(limit)

        return [
            {
                "entity_type": r["entity_type"],
                "entity_value": r["entity_value"],
                "occurrence_count": r["occurrence_count"],
                "last_seen": r["last_seen"].isoformat() if isinstance(r["last_seen"], datetime) else str(r["last_seen"]),
                "crime_types": r["crime_types"],
                "risk_score": r["risk_score"],
                "is_confirmed_threat": r["is_confirmed_threat"]
            }
            for r in results
        ]
