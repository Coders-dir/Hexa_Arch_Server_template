import asyncio
import time
from tests.fake_redis import FakeRedis, FakeAsyncRedis


def test_expire_and_get_set():
    r = FakeRedis()
    r.set('k', 'v', ex=1)
    assert r.get('k') == 'v'
    time.sleep(1.1)
    assert r.get('k') is None


def test_incr_and_expire():
    r = FakeRedis()
    assert r.incr('cnt') == 1
    assert r.incr('cnt') == 2
    r.expire('cnt', 1)
    assert r.get('cnt') == 2
    time.sleep(1.1)
    assert r.get('cnt') is None


async def _async_work():
    ar = FakeAsyncRedis()
    await ar.set('a', 'b', ex=1)
    v = await ar.get('a')
    assert v == 'b'
    await asyncio.sleep(1.1)
    v2 = await ar.get('a')
    assert v2 is None


def test_async_set_get_loop():
    asyncio.get_event_loop().run_until_complete(_async_work())
