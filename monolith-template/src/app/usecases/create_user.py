from ..domain.user import User
from src.app.ports.repositories import UserRepository


async def create_user(repo: UserRepository, email: str, name: str | None = None) -> User:
    """Create a new user via the repository port (async).

    Uses the domain factory `User.create` and delegates persistence to the repository port.
    """
    user = User.create(email=email, name=name)
    await repo.create(user)
    return user
