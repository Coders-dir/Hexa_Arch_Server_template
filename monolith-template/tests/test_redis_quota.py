import asyncio
import os

import pytest

from src.app.adapters.outbound.redis_quota import QuotaManager


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_consume_allows_and_blocks():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    key = "testkey"
    # ensure base
    allowed = []
    for _ in range(3):
        ok = await qm.consume(key, window=2, limit=2)
        allowed.append(ok)
    # first two allowed True, third False within the 2s window
    assert allowed[0] is True
    assert allowed[1] is True
    assert allowed[2] is False
    await qm.close()
