import asyncio
from src.app.adapters.outbound.cache.redis_quota import QuotaManager


def test_quota_manager_degraded_mode():
    async def run():
        qm = QuotaManager()
        # simulate degraded mode (no redis client)
        qm._client = None

        # consume should allow by default in degraded mode
        allowed = await qm.consume("k", 60, 10)
        assert allowed is True

        # queue push/pop should use in-memory fallback
        await qm.push_queue_priority("q", "payload1", priority=5)
        await qm.push_queue_priority("q", "payload2", priority=1)
        val = await qm.pop_queue_priority("q")
        assert val in ("payload1", "payload2")

        # circuit breaker helpers are no-ops and should not raise
        assert (await qm.is_circuit_open("prov")) is False
        await qm.record_failure("prov")
        await qm.record_success("prov")

    asyncio.run(run())
