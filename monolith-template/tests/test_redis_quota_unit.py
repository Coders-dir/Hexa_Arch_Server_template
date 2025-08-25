import asyncio
import os
import pytest

from src.app.adapters.outbound.redis_quota import QuotaManager


@pytest.mark.asyncio
async def test_quota_manager_priority_and_delay():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    q = "test:unit:priority"
    # clear
    await qm._client.delete(q)

    # push: smaller priority value is higher priority
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


@pytest.mark.asyncio
async def test_quota_manager_consume_rate_limit():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    key = "unit-test-consume"
    # try a small window of 1s with limit of 2
    ok1 = await qm.consume(key, window=1, limit=2)
    ok2 = await qm.consume(key, window=1, limit=2)
    ok3 = await qm.consume(key, window=1, limit=2)

    assert ok1 is True
    assert ok2 is True
    assert ok3 is False

    await qm.close()
