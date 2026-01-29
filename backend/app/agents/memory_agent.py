import json
from backend.app.schemas.common import ScamAnalysisResult
from backend.app.mcp_servers.memory.server import store_scam_case

async def update_memory(result: ScamAnalysisResult):
    """
    Agent responsible for ingesting the final result into the collective memory.
    """
    # Call the MCP tool
    await store_scam_case(result)
    
    return "Memory updated."
