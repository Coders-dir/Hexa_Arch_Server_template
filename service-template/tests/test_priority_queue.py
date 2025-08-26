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
async def test_priority_and_delay():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    q = "dispatcher:priority_queue"
    # clear
    await qm._client.delete(q)
    await qm.push_queue_priority(q, "low", priority=10, delay=0)
    await qm.push_queue_priority(q, "high", priority=1, delay=0)
    await qm.push_queue_priority(q, "delayed", priority=0, delay=2)

    first = await qm.pop_queue_priority(q)
    assert first == "high"
    second = await qm.pop_queue_priority(q)
    assert second == "low"
    # delayed not yet ready
    third = await qm.pop_queue_priority(q)
    assert third is None
    await asyncio.sleep(2.1)
    third2 = await qm.pop_queue_priority(q)
    assert third2 == "delayed"
    await qm.close()
