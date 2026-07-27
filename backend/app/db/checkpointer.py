import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Budget explicit time for asyncpg + nest_asyncio concurrency handling
def get_checkpointer():
    """
    Returns Postgres-backed checkpointer if DATABASE_URL is configured,
    with asyncpg + nest_asyncio concurrency protection.
    Falls back gracefully to MemorySaver if Postgres connection is unavailable.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and ("postgresql" in database_url or "postgres" in database_url):
        try:
            import importlib
            nest_asyncio_mod = importlib.import_module("nest_asyncio")
            nest_asyncio_mod.apply()
            
            postgres_aio = importlib.import_module("langgraph.checkpoint.postgres.aio")
            AsyncPostgresSaver = getattr(postgres_aio, "AsyncPostgresSaver")
            
            psycopg_pool_mod = importlib.import_module("psycopg_pool")
            AsyncConnectionPool = getattr(psycopg_pool_mod, "AsyncConnectionPool")
            
            print(f"[Checkpointer] Connecting Postgres Saver at {database_url.split('@')[-1] if '@' in database_url else 'local'}")
            pool = AsyncConnectionPool(conninfo=database_url, max_size=20)
            checkpointer = AsyncPostgresSaver(pool)
            return checkpointer
        except Exception as e:
            logger.warning(f"[Checkpointer] Could not initialize PostgresSaver ({e}). Falling back to MemorySaver.")
            
    from langgraph.checkpoint.memory import MemorySaver
    print("[Checkpointer] Using MemorySaver checkpointer.")
    return MemorySaver()
