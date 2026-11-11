# backend/app/database.py
"""Database connection utilities.
Uses asyncpg connection pool.
Provides a FastAPI dependency ``get_db`` that yields a connection.
"""

import os
import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
from typing import AsyncGenerator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/campuseats")

_pool: Pool | None = None

async def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)

async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    if _pool is None:
        await init_pool()

    async with _pool.acquire() as conn:
        async with conn.transaction():
            yield conn