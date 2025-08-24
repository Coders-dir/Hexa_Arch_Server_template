from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from src.app.ports.repositories import UserRepository
from src.app.domain.user import User

class MongoUserRepo(UserRepository):
    def __init__(self, client: AsyncIOMotorClient, db_name: str = "app_db"):
        self._db = client[db_name]

    async def create(self, user: User) -> None:
        await self._db.users.insert_one({"_id": user.id, "email": user.email, "name": user.name, "created_at": user.created_at})

    async def find_by_id(self, user_id: str) -> Optional[User]:
        row = await self._db.users.find_one({"_id": user_id})
        if not row:
            return None
        return User(id=row["_id"], email=row["email"], name=row.get("name"), created_at=row.get("created_at"))
