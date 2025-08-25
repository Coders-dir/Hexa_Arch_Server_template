import os
import time
from typing import Optional, Any

try:
    import redis.asyncio as redis
except Exception:
    # If redis isn't available at type-check or runtime, fallback to None for runtime checks.
    redis = None  # type: ignore

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")


class QuotaManager:
    """Minimal Redis-based quota & priority/delay queue helpers.

    Score encoding for the priority queue: float(timestamp + delay) + small priority offset.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or REDIS_URL
        # typed as Any to satisfy mypy for dynamic client assignment in init()
        self._client: Any = None

    async def init(self) -> None:
        if redis is None:
            raise RuntimeError("redis.asyncio not available; install 'redis' package")
        self._client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

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
        now = int(time.time())
        bucket = f"quota:{key}:{window}:{now // window}"
        val = await self._client.incr(bucket)
        if val == 1:
            await self._client.expire(bucket, window)
        return val <= limit

    async def push_queue_priority(self, queue_name: str, payload: str, priority: int = 0, delay: int = 0) -> None:
        # Use integer-second base so items pushed within the same second share the same base
        base_sec = int(time.time()) + int(delay)
        # Compose integer score: seconds * 10000 + priority. Smaller score == higher priority.
        composite = int(base_sec) * 10000 + int(priority)
        member = f"{int(priority)}::{payload}"
        await self._client.zadd(queue_name, {member: composite})

    async def pop_queue_priority(self, queue_name: str) -> Optional[str]:
        """Atomically pop the lowest-score member whose score <= now*10000 using Lua.

        We use integer composite scores: (seconds * 10000) + priority. Smaller score == higher priority.
        """
        # Treat 'now' as the end of the current second so items pushed in the same second are eligible
        now_tick = int(time.time()) * 10000 + 9999
        lua = """
        local items = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1], 'LIMIT', 0, 100)
        if #items == 0 then
            return nil
        end
        -- choose the item with smallest numeric score (ZRANGEBYSCORE already returns in score order)
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

    async def record_failure(self, provider: str, window: int = 60, max_failures: int = 5, cooldown: int = 60) -> None:
        now = int(time.time())
        failures_key = f"cb:failures:{provider}:{now // window}"
        val = await self._client.incr(failures_key)
        if val == 1:
            await self._client.expire(failures_key, window)
        if val >= max_failures:
            open_key = f"cb:open:{provider}"
            await self._client.set(open_key, "1", ex=cooldown)

    async def is_circuit_open(self, provider: str) -> bool:
        open_key = f"cb:open:{provider}"
        val = await self._client.get(open_key)
        return val is not None

    async def record_success(self, provider: str) -> None:
        open_key = f"cb:open:{provider}"
        await self._client.delete(open_key)
