import os
import time
try:
    import redis.asyncio as redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")


class QuotaManager:
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or REDIS_URL
        self._client = None

    async def init(self):
        if redis is None:
            raise RuntimeError("redis.asyncio not available; install 'redis' package")
        self._client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        # load scripts
        try:
            from src.app.adapters.outbound.redis_scripts import QUOTA_SCRIPT

            self._quota_sha = await self._client.script_load(QUOTA_SCRIPT)
        except Exception:
            self._quota_sha = None

    async def close(self):
        if self._client:
            # use aclose() to properly close async redis client
            try:
                await self._client.aclose()
            except Exception:
                try:
                    # fallback for older redis versions
                    self._client.close()
                except Exception:
                    pass

    async def consume(self, key: str, window: int, limit: int) -> bool:
        """Consume a token for key in a sliding window (seconds). Returns True if allowed."""
        now = int(time.time())
        redis_key = f"quota:{key}"
        try:
            if self._quota_sha:
                res = await self._client.evalsha(self._quota_sha, 1, redis_key, window, limit, now)
                return bool(res)
        except Exception:
            # fallback to safe incr
            pass

        bucket = f"quota:{key}:{window}:{now // window}"
        val = await self._client.incr(bucket)
        if val == 1:
            await self._client.expire(bucket, window)
        return val <= limit

    async def push_queue(self, queue_name: str, payload: str):
        # legacy FIFO push
        await self._client.rpush(queue_name, payload)

    async def push_queue_priority(self, queue_name: str, payload: str, priority: int = 0, delay: int = 0):
        """Push payload into a sorted set queue with priority (lower is higher priority) and optional delay in seconds."""
        base = int(time.time()) + delay
        # combine priority into score: primary sort by base (time+delay), secondary by priority
        # encode as base*1000 + priority so that lower priority value sorts first
        composite = int(base) * 1000 + int(priority)
        member = f"{int(priority)}::" + payload
        await self._client.zadd(queue_name, {member: composite})

    async def pop_queue_priority(self, queue_name: str):
        """Pop the lowest-score item from the sorted set atomically.

        Prefer ZPOPMIN (available in Redis >= 5.0) for atomic removal. If not
        available, fall back to a safe pipeline: find eligible items by score,
        choose best by priority, then ZREM the chosen member.
        """
        now = int(time.time())
        # Try ZPOPMIN with maxcount=1 after filtering by score using ZRANGEBYSCORE
        try:
            popped = await self._client.zpopmin(queue_name, count=1)
            if popped:
                member, score = popped[0]
                # composite scores are base*1000 + priority; compute threshold for now
                threshold = now * 1000 + 999
                if score <= threshold:
                    try:
                        return member.split("::", 1)[1]
                    except Exception:
                        return member
                # popped an item scheduled for the future — re-add it and return None
                await self._client.zadd(queue_name, {member: score})
                return None
        except Exception:
            # fall through to safe fallback
            pass

        # Fallback: read eligible items up to now (use composite threshold)
        max_threshold = now * 1000 + 999
        items = await self._client.zrangebyscore(queue_name, min=-1e18, max=max_threshold, start=0, num=100)
        if not items:
            return None
        best = None
        best_prio = None
        for m in items:
            try:
                pr, _ = m.split("::", 1)
                pr = int(pr)
            except Exception:
                pr = 0
            if best is None or pr < best_prio:
                best = m
                best_prio = pr
        if best is None:
            return None
        removed = await self._client.zrem(queue_name, best)
        if removed:
            return best.split("::", 1)[1]
        return None

    # Circuit breaker helpers
    async def record_failure(self, provider: str, window: int = 60, max_failures: int = 5, cooldown: int = 60):
        """Record a failure for a provider. If failures exceed max_failures within window, open circuit for cooldown seconds."""
        now = int(time.time())
        failures_key = f"cb:failures:{provider}:{now // window}"
        val = await self._client.incr(failures_key)
        if val == 1:
            await self._client.expire(failures_key, window)
        # count failures across recent windows
        # simple approach: sum current bucket only
        if val >= max_failures:
            open_key = f"cb:open:{provider}"
            await self._client.set(open_key, "1", ex=cooldown)

    async def is_circuit_open(self, provider: str) -> bool:
        open_key = f"cb:open:{provider}"
        val = await self._client.get(open_key)
        return val is not None

    async def record_success(self, provider: str):
        # clear failure buckets and open flag
        open_key = f"cb:open:{provider}"
        await self._client.delete(open_key)
