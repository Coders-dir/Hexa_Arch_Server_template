from src.app.ports.repositories import UserRepository
from src.app.usecases.create_user import create_user
from src.app.domain.user import User


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def create(self, email: str, name: str | None = None) -> User:
        return await create_user(self._repo, email=email, name=name)
