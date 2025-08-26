import pytest

from src.app.adapters.outbound.inmemory_user_repo import InMemoryUserRepo
from src.app.adapters.outbound.supabase_client import SupabaseClient
from src.app.adapters.outbound.mongo_user_repo import MongoUserRepo
from src.app.adapters.outbound.postgres_user_repo import PostgresUserRepo
from src.app.services.user_service import UserService


class DummySupabaseClient:
    def __init__(self):
        self._store = []

    async def insert(self, table, payload):
        self._store.append(payload)
        return payload

    async def select(self, table, filters=""):
        return self._store


@pytest.mark.asyncio
async def test_supabase_adapter_mocked(monkeypatch):
    dummy = DummySupabaseClient()
    monkeypatch.setenv("SUPABASE_URL", "https://example.invalid")
    monkeypatch.setenv("SUPABASE_API_KEY", "fake-key")

    # monkeypatch the real client to use our dummy
    monkeypatch.setattr("src.app.adapters.outbound.supabase_client.SupabaseClient.__init__", lambda self, url=None, key=None: setattr(self, '_client', dummy) or setattr(self, 'insert', dummy.insert) or setattr(self, 'select', dummy.select) or None)

    client = SupabaseClient()
    await client.insert("users", {"email": "a@b.com"})
    rows = await client.select("users")
    assert rows and rows[0]["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_inmemory_repo_and_service():
    repo = InMemoryUserRepo()
    svc = UserService(repo)
    user = await svc.create(email="u@example.com", name="u")
    fetched = await repo.find_by_id(user.id)
    assert fetched is not None


def test_postgres_and_mongo_placeholders():
    # These adapters are placeholders and should be integration-tested against real services.
    assert PostgresUserRepo
    assert MongoUserRepo
