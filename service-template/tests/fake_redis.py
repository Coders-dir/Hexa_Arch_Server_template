import asyncio
import time


class FakeRedis:
    def __init__(self, *args, **kwargs):
        # store holds simple key->value mappings for strings and dicts for zsets
        self.store = {}
        # expirations holds key->expire_timestamp (epoch seconds)
        self._expirations = {}

    def _cleanup_expired(self):
        now = time.time()
        expired = [k for k, ts in self._expirations.items() if ts is not None and ts <= now]
        for k in expired:
            self.store.pop(k, None)
            self._expirations.pop(k, None)

    def ping(self):
        return True

    def delete(self, *keys):
        self._cleanup_expired()
        for k in keys:
            self.store.pop(k, None)
            self._expirations.pop(k, None)
        return True

    def set(self, key, value, ex=None):
        self._cleanup_expired()
        self.store[key] = value
        if ex is not None:
            self._expirations[key] = time.time() + int(ex)
        else:
            self._expirations.pop(key, None)
        return True

    def get(self, key):
        self._cleanup_expired()
        return self.store.get(key)

    def expire(self, key, seconds):
        self._cleanup_expired()
        if key in self.store:
            self._expirations[key] = time.time() + int(seconds)
            return True
        return False

    def incr(self, key):
        self._cleanup_expired()
        v = int(self.store.get(key, 0)) + 1
        self.store[key] = v
        return v

    def zadd(self, name, mapping):
        self._cleanup_expired()
        # mapping: {member: score}
        z = self.store.setdefault(name, {})
        for member, score in mapping.items():
            z[member] = int(score)
        return True

    def zrangebyscore(self, name, min_score, max_score, start=0, num=None):
        self._cleanup_expired()
        z = self.store.get(name, {})
        items = [(m, s) for m, s in z.items() if s >= int(min_score) and s <= int(max_score)]
        items.sort(key=lambda kv: kv[1])
        members = [m for m, s in items]
        if num is None:
            return members[start:]
        return members[start:start + int(num)]

    def zrange(self, name, start, end, withscores=False):
        self._cleanup_expired()
        z = self.store.get(name, {})
        items = sorted(z.items(), key=lambda kv: kv[1])
        members = [m for m, s in items]
        # Redis end is inclusive
        return members[start:end+1]

    def zpopmin(self, name, count=1):
        self._cleanup_expired()
        z = self.store.get(name, {})
        items = sorted(z.items(), key=lambda kv: kv[1])
        popped = []
        for _ in range(min(count, len(items))):
            m, s = items.pop(0)
            popped.append((m, s))
            z.pop(m, None)
        return popped

    def eval(self, script, numkeys, *keys_and_args):
        # Minimal emulation for the specific Lua used in QuotaManager.pop_queue_priority
        self._cleanup_expired()
        if numkeys < 1:
            return None
        key = keys_and_args[0]
        # arg for max score
        try:
            max_score = int(keys_and_args[1])
        except Exception:
            return None
        # emulate ZRANGEBYSCORE key -inf max LIMIT 0 100
        members = self.zrangebyscore(key, -10**18, max_score, start=0, num=100)
        if not members:
            return None
        best = members[0]
        # remove it
        z = self.store.get(key, {})
        removed = 1 if z.pop(best, None) is not None else 0
        if removed == 1:
            return best
        return None

    def close(self):
        return True


class FakeAsyncRedis(FakeRedis):
    async def ping(self):
        return True

    async def delete(self, *keys):
        return super().delete(*keys)

    async def incr(self, key):
        return super().incr(key)

    async def zadd(self, name, mapping):
        return super().zadd(name, mapping)

    async def zrange(self, name, start, end, withscores=False):
        return super().zrange(name, start, end, withscores)

    async def zpopmin(self, name, count=1):
        return super().zpopmin(name, count)

    async def eval(self, script, numkeys, *keys_and_args):
        return super().eval(script, numkeys, *keys_and_args)

    async def get(self, key):
        return super().get(key)

    async def set(self, key, value, ex=None):
        return super().set(key, value, ex=ex)

    async def expire(self, key, seconds):
        return super().expire(key, seconds)

    async def aclose(self):
        return True

    async def close(self):
        return True


# helper factory
def get_fake_client(asyncio_mode=False, *args, **kwargs):
    return FakeAsyncRedis() if asyncio_mode else FakeRedis()
