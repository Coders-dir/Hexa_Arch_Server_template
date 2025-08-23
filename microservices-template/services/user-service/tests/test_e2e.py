import pytest
from httpx import AsyncClient, ASGITransport
from src.app.main import app


@pytest.mark.asyncio
async def test_health_and_user_route():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200

        r2 = await ac.get("/api/users/abc")
        assert r2.status_code == 200
        assert r2.json()["id"] == "abc"
