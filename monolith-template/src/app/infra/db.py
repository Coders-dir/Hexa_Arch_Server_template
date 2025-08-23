from motor.motor_asyncio import AsyncIOMotorClient
from src.app.infra.config import settings

_db = None

async def init_db():
    global _db
    if _db is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required")
        client = AsyncIOMotorClient(settings.database_url)
        _db = client.get_default_database()
    return _db

async def get_db():
    if _db is None:
        await init_db()
    return _db
