import asyncio
import os

import pytest

from src.app.adapters.outbound.redis_quota import QuotaManager


@pytest.mark.asyncio
async def test_scheduler_worker_processes_priority_queue():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    queue = "test:scheduler:queue"
    await qm._client.delete(queue)

    # push items: low, high, med
    await qm.push_queue_priority(queue, "item-low", priority=10)
    await qm.push_queue_priority(queue, "item-high", priority=1)
    await qm.push_queue_priority(queue, "item-med", priority=5)

    processed = []

    async def worker():
        while len(processed) < 3:
            v = await qm.pop_queue_priority(queue)
            if v:
                processed.append(v)
            else:
                await asyncio.sleep(0.05)

    # run worker with timeout
    task = asyncio.create_task(worker())
    try:
        await asyncio.wait_for(task, timeout=5)
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except Exception:
                pass

    assert processed == ["item-high", "item-med", "item-low"]

    await qm.close()
