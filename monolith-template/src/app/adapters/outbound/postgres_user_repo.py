from typing import Optional

from src.app.ports.repositories import UserRepository
from src.app.domain.user import User

# Minimal async Postgres adapter example using asyncpg or an async ORM
# This is a placeholder example; adapt for your chosen DB layer (SQLAlchemy async, GINO, etc.)

class PostgresUserRepo(UserRepository):
    def __init__(self, pool):
        self._pool = pool

    async def create(self, user: User) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("INSERT INTO users (id, email, name, created_at) VALUES ($1,$2,$3,$4)", user.id, user.email, user.name, user.created_at)

    async def find_by_id(self, user_id: str) -> Optional[User]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT id, email, name, created_at FROM users WHERE id=$1", user_id)
            if not row:
                return None
            return User(id=row[0], email=row[1], name=row[2], created_at=row[3])
