from typing import List, Optional
from src.app.ports.repositories import UserRepository
from src.app.domain.user import User


class InMemoryUserRepo(UserRepository):
    def __init__(self):
        self._data: List[User] = []
        self._next = 1

    async def create(self, user: User) -> None:
        if user.id is None:
            user.id = str(self._next)
            self._next += 1
        self._data.append(user)

    async def find_by_id(self, id: str) -> Optional[User]:
        for u in self._data:
            if u.id == id:
                return u
        return None
