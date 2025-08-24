import pytest

from src.app.adapters.outbound.inmemory_user_repo import InMemoryUserRepo
from src.app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user():
    repo = InMemoryUserRepo()
    svc = UserService(repo)
    user = await svc.create(email="alice@example.com", name="alice")
    assert user.id is not None
    assert user.email == "alice@example.com"
    fetched = await repo.find_by_id(user.id)
    assert fetched is not None
