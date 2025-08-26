import asyncio
import signal

from prometheus_client import Counter, Gauge

from src.app.adapters.outbound.redis_quota import QuotaManager


STOP = False


def _signal_handler(sig, frame):
    global STOP
    print("worker: received signal, shutting down")
    STOP = True


async def main(loop_sleep: float = 0.2):
    qm = QuotaManager()
    await qm.init()
    # Prometheus metrics
    processed_jobs = Counter("worker_processed_jobs_total", "Total processed jobs by worker")
    queue_depth = Gauge("dispatcher_queue_depth", "Current dispatcher priority queue depth")

    print("worker: started, waiting for items in dispatcher:priority_queue")

    try:
        while not STOP:
            try:
                val = await qm.pop_queue_priority("dispatcher:priority_queue")
                if val:
                    print("worker: processed", val)
                    try:
                        processed_jobs.inc()
                    except Exception:
                        pass
                else:
                    await asyncio.sleep(loop_sleep)
            except Exception as e:
                print("worker: error processing item", e)
                await asyncio.sleep(1)
            # update queue depth if client available
            try:
                if getattr(qm, "_client", None):
                    try:
                        depth = await qm._client.zcard("dispatcher:priority_queue")
                        queue_depth.set(int(depth or 0))
                    except Exception:
                        pass
            except Exception:
                pass
    finally:
        await qm.close()
        print("worker: shutdown complete")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    asyncio.run(main())
