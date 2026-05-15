from typing import List, Dict, Any
from backend.app.db.mongodb import db

class MemoryService:
    @staticmethod
    async def find_linked_cases(entity_value: str) -> List[Dict[str, Any]]:
        """
        Searches historical cases for the same entity (wallet, phone, etc.).
        """
        # This assumes we have an 'entities' collection or indexed fields in cases
        # For now, we simulate a match
        cursor = db.get_collection("cases").find({"entities.value": entity_value})
        results = await cursor.to_list(length=10)
        return results

    @staticmethod
    async def get_longitudinal_insights(case_id: str, entities: List[Dict[str, Any]]) -> List[str]:
        """
        Generates cross-case intelligence.
        """
        insights = []
        for entity in entities:
            matches = await MemoryService.find_linked_cases(entity['value'])
            if matches:
                insights.append(f"Entity {entity['value']} was previously linked to {len(matches)} other incidents.")
        
        return insights
