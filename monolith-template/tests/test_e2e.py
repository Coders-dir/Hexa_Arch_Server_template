import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from src.app.main import app


@pytest.mark.asyncio
async def test_create_and_get_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/users/", json={"email": "alice@example.com", "name": "Alice"})
        assert r.status_code == 201
        payload = r.json()
        user_id = payload["id"]

        r2 = await ac.get(f"/api/users/{user_id}")
        assert r2.status_code == 200
        data = r2.json()
        assert data["id"] == user_id
