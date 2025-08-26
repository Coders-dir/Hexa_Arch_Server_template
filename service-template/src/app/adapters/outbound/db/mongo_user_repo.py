from src.app.ports.repositories import UserRepository
from src.app.domain.user import User

class MongoUserRepository(UserRepository):
    def __init__(self, db):
        self._db = db

    async def create(self, user: User) -> None:
        await self._db.users.insert_one(user.__dict__)

    async def find_by_id(self, user_id: str) -> User | None:
        data = await self._db.users.find_one({"id": user_id})
        from src.app.ports.repositories import UserRepository
        from src.app.domain.user import User


        class MongoUserRepository(UserRepository):
            def __init__(self, db):
                self._db = db

            async def create(self, user: User) -> None:
                await self._db.users.insert_one(user.__dict__)

            async def find_by_id(self, user_id: str) -> User | None:
                data = await self._db.users.find_one({"id": user_id})
                if not data:
                    return None
                return User(**data)
