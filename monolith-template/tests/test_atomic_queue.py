import asyncio
import os

import pytest

from src.app.adapters.outbound.redis_quota import QuotaManager


@pytest.mark.asyncio
async def test_atomic_pop_priority():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    queue = "test:atomic:queue"
    # cleanup
    await qm._client.delete(queue)

    # push items with different priorities and no delay
    await qm.push_queue_priority(queue, "item-low", priority=10)
    await qm.push_queue_priority(queue, "item-high", priority=1)
    await qm.push_queue_priority(queue, "item-med", priority=5)

    # atomic pop should return the highest priority (lowest number)
    first = await qm.pop_queue_priority(queue)
    assert first == "item-high"

    second = await qm.pop_queue_priority(queue)
    assert second == "item-med"

    third = await qm.pop_queue_priority(queue)
    assert third == "item-low"

    # empty now
    none = await qm.pop_queue_priority(queue)
    assert none is None

    await qm.close()
