from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.app.infra.config import settings

# The application's motor database instance (initialized lazily)
_db: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required")
        client: AsyncIOMotorClient = AsyncIOMotorClient(settings.database_url)
        _db = client.get_default_database()
    assert _db is not None
    return _db


async def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        await init_db()
    assert _db is not None
    return _db
