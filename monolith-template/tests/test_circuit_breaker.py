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
async def test_circuit_opens_and_closes():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    provider = "test-provider"
    # ensure clean
    await qm._client.delete(f"cb:open:{provider}")
    # record failures
    for _ in range(5):
        await qm.record_failure(provider, window=10, max_failures=3, cooldown=2)
    is_open = await qm.is_circuit_open(provider)
    assert is_open is True
    # wait for cooldown
    await asyncio.sleep(2.5)
    is_open2 = await qm.is_circuit_open(provider)
    assert is_open2 is False
    await qm.close()
