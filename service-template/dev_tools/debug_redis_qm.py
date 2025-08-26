import asyncio
import os
import time
from src.app.adapters.outbound.redis_quota import QuotaManager

async def dump(qm, q, label):
    items = await qm._client.zrange(q, 0, -1, withscores=True)
    print(f"{label} zrange (all):", items)
    items2 = await qm._client.zrangebyscore(q, min=-1e18, max=time.time(), withscores=True)
    print(f"{label} zrangebyscore (<=now):", items2)
    try:
        server_time = await qm._client.time()
        print(f"{label} server TIME:", server_time)
    except Exception as e:
        print("could not fetch server time:", e)

async def info_key(qm, q, label):
    try:
        ex = await qm._client.exists(q)
        t = await qm._client.ttl(q)
        typ = await qm._client.type(q)
        print(f"{label} key exists={ex}, ttl={t}, type={typ}")
    except Exception as e:
        print("could not fetch key info:", e)

async def main():
    qm = QuotaManager(redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    await qm.init()
    q = "dispatcher:priority_queue"
    print("clearing queue")
    await qm._client.delete(q)
    await qm.push_queue_priority(q, "low", priority=10, delay=0)
    await qm.push_queue_priority(q, "high", priority=1, delay=0)
    await qm.push_queue_priority(q, "delayed", priority=0, delay=2)
    print("pushed items")
    await dump(qm, q, 'after push')
    await info_key(qm, q, 'after push')

    first = await qm.pop_queue_priority(q)
    print("first:", first)
    await dump(qm, q, 'after first pop')
    await info_key(qm, q, 'after first pop')
    second = await qm.pop_queue_priority(q)
    print("second:", second)
    await dump(qm, q, 'after second pop')
    await info_key(qm, q, 'after second pop')
    third = await qm.pop_queue_priority(q)
    print("third (immediate):", third)
    await dump(qm, q, 'after third pop')
    await info_key(qm, q, 'after third pop')
    print("sleeping 2.1s")
    await asyncio.sleep(2.1)
    await dump(qm, q, 'after sleep')
    await info_key(qm, q, 'after sleep')
    # check zscore of delayed member
    z = await qm._client.zscore(q, '0::delayed')
    print('zscore delayed after sleep:', z)
    third2 = await qm.pop_queue_priority(q)
    print("third (after sleep):", third2)
    await dump(qm, q, 'after final pop')
    await info_key(qm, q, 'after final pop')

    await qm.close()

if __name__ == '__main__':
    asyncio.run(main())
