import os
import time
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Pre-declare `redis` as Any so static checkers don't infer a Module|None union
redis: Any = None
try:
    import redis.asyncio as redis
except Exception:
    # If redis isn't available at runtime, keep redis as None and tolerate it at init()
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")


class QuotaManager:
    """Redis-backed quota & priority queue helpers with an in-memory fallback.

    The implementation prefers Redis but will operate in a degraded in-memory mode
    when redis is not available or initialization failed. This prevents startup
    handlers from blocking the application when external services are transient.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or REDIS_URL
        # client is assigned at init(); keep unannotated to avoid analyzer issues
        self._client: Any = None
        # in-memory fallback queue for priority items when redis isn't available
        self._in_memory_queue: list[str] = []

    async def init(self) -> None:
        """Attempt to initialize the redis client; do not raise on failure.

        This method sets the internal client when possible. Callers should not
        treat failure to connect as fatal; methods below handle the degraded
        in-memory mode.
        """
        if redis is None:
            logger.info("QuotaManager: redis.asyncio not present; using in-memory fallback")
            return
        try:
            self._client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
            logger.info("QuotaManager: redis client initialized")
        except Exception as e:
            logger.warning("QuotaManager: failed to initialize redis client: %s", e)
            self._client = None

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                try:
                    self._client.close()
                except Exception:
                    pass

    async def consume(self, key: str, window: int, limit: int) -> bool:
        """Best-effort consume. Returns True (allowed) when backend not available."""
        if not self._client:
            # degraded mode: optimistically allow
            return True
        now = int(time.time())
        bucket = f"quota:{key}:{window}:{now // window}"
        val = await self._client.incr(bucket)
        if val == 1:
            await self._client.expire(bucket, window)
        return val <= limit

    async def push_queue_priority(self, queue_name: str, payload: str, priority: int = 0, delay: int = 0) -> None:
        if not self._client:
            # append an encoded member to in-memory queue for best-effort processing
            member = f"{int(priority)}::{payload}"
            self._in_memory_queue.append((int(priority), member))
            return
        base_sec = int(time.time()) + int(delay)
        composite = int(base_sec) * 10000 + int(priority)
        member = f"{int(priority)}::{payload}"
        await self._client.zadd(queue_name, {member: composite})

    async def pop_queue_priority(self, queue_name: str) -> Optional[str]:
        # Redis path
        if self._client:
            now_tick = int(time.time()) * 10000 + 9999
            lua = """
            local items = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1], 'LIMIT', 0, 100)
            if #items == 0 then
                return nil
            end
            local best = items[1]
            local removed = redis.call('ZREM', KEYS[1], best)
            if removed == 1 then
                return best
            end
            return nil
            """
            try:
                res = await self._client.eval(lua, 1, queue_name, str(now_tick))
            except Exception:
                res = None
            if not res:
                return None
            try:
                return res.split('::', 1)[1] if '::' in res else res
            except Exception:
                return res

        # In-memory fallback: return the highest priority (smallest priority value)
        if not self._in_memory_queue:
            return None
        # sort by priority then pop first
        self._in_memory_queue.sort(key=lambda t: t[0])
        _, member = self._in_memory_queue.pop(0)
        try:
            return member.split('::', 1)[1] if '::' in member else member
        except Exception:
            return member

    async def record_failure(self, provider: str, window: int = 60, max_failures: int = 5, cooldown: int = 60) -> None:
        if not self._client:
            # no-op in degraded mode
            return
        now = int(time.time())
        failures_key = f"cb:failures:{provider}:{now // window}"
        val = await self._client.incr(failures_key)
        if val == 1:
            await self._client.expire(failures_key, window)
        if val >= max_failures:
            open_key = f"cb:open:{provider}"
            await self._client.set(open_key, "1", ex=cooldown)

    async def is_circuit_open(self, provider: str) -> bool:
        if not self._client:
            return False
        open_key = f"cb:open:{provider}"
        val = await self._client.get(open_key)
        return val is not None

    async def record_success(self, provider: str) -> None:
        if not self._client:
            return
        open_key = f"cb:open:{provider}"
        await self._client.delete(open_key)
