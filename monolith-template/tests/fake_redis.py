import asyncio

class FakeRedis:
    def __init__(self, *args, **kwargs):
        self.store = {}

    def ping(self):
        return True

    def delete(self, *keys):
        for k in keys:
            self.store.pop(k, None)
        return True

    def zadd(self, name, mapping):
        # mapping: {member: score}
        z = self.store.setdefault(name, {})
        for member, score in mapping.items():
            z[member] = score
        return True

    def zrange(self, name, start, end, withscores=False):
        z = self.store.get(name, {})
        items = sorted(z.items(), key=lambda kv: kv[1])
        members = [m for m, s in items]
        return members[start:end+1]

    def zpopmin(self, name, count=1):
        z = self.store.get(name, {})
        items = sorted(z.items(), key=lambda kv: kv[1])
        popped = []
        for _ in range(min(count, len(items))):
            m, s = items.pop(0)
            popped.append((m, s))
            z.pop(m, None)
        return popped

class FakeAsyncRedis(FakeRedis):
    async def ping(self):
        return True

    async def delete(self, *keys):
        return super().delete(*keys)

    async def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    async def zadd(self, name, mapping):
        return super().zadd(name, mapping)

    async def zrange(self, name, start, end, withscores=False):
        return super().zrange(name, start, end, withscores)

    async def zpopmin(self, name, count=1):
        return super().zpopmin(name, count)

    async def close(self):
        return True

# helper factory
def get_fake_client(asyncio_mode=False, *args, **kwargs):
    return FakeAsyncRedis() if asyncio_mode else FakeRedis()
