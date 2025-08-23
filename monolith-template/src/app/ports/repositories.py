from abc import ABC, abstractmethod
from typing import Protocol
from src.app.domain.user import User

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError()
