import os
import json
import asyncpg
import asyncio
import logging
import random
from typing import List
from prometheus_client import Counter

logger = logging.getLogger(__name__)
import os
import json
import asyncpg
import asyncio
import logging
import random
from typing import List
from prometheus_client import Counter

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:test@127.0.0.1:5432/test_db")

# Prometheus counter for pool init failures
POOL_INIT_FAILURES = Counter("api_key_repo_pool_init_failures_total", "Total number of pool init failures")


def get_metrics():
    """Return a minimal metrics dict for handoff endpoints."""
    try:
        value = int(POOL_INIT_FAILURES._value.get())
    except Exception:
        value = 0
    return {"pool_init_failures": value}


class ApiKeyRepo:
    """Postgres-backed API key repository using an asyncpg pool managed on app startup.

    Methods assume the pool is initialized via `await repo.init()` and closed via
    `await repo.close()` during application lifecycle events.
    """

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or DATABASE_URL
        self._pool: asyncpg.pool.Pool | None = None

    async def init(self) -> None:
        """Initialize an asyncpg pool with exponential backoff and jitter.

        SSL is disabled for local test Postgres. On repeated failure the
        Prometheus counter is incremented and the last exception is raised.
        """
        max_attempts = 6
        base = 0.2
        last_err = None
        for attempt in range(1, max_attempts + 1):
            try:
                self._pool = await asyncpg.create_pool(self.dsn, ssl=False)
                logger.info("ApiKeyRepo: pool initialized")
                return
            except Exception as e:  # keep broad to surface connectivity issues
                last_err = e
                sleep = base * (2 ** (attempt - 1))
                jitter = random.uniform(-0.2 * sleep, 0.2 * sleep)
                delay = min(5.0, sleep + jitter)
                logger.warning(
                    "ApiKeyRepo: pool init attempt %d failed (%s), retrying in %.2fs",
                    attempt,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)

        logger.error("ApiKeyRepo: pool init failed after %d attempts: %s", max_attempts, last_err)
        try:
            POOL_INIT_FAILURES.inc()
        except Exception:
            logger.debug("ApiKeyRepo: failed to increment POOL_INIT_FAILURES metric")
        raise last_err

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def create_key(self, kid: str, name: str | None, owner: str | None, scopes: List[str], hashed_token: str) -> None:
        """Insert a new API key row. If pool isn't available, fall back to a per-call connection.

        Scopes are stored as JSONB; ensure we pass a JSON string to the query.
        """
        if not self._pool:
            conn = None
            last_err = None
            for attempt in range(1, 5):
                try:
                    conn = await asyncpg.connect(self.dsn, ssl=False)
                    break
                except Exception as e:
                    last_err = e
                    delay = 0.1 * (2 ** (attempt - 1))
                    jitter = random.uniform(-0.1 * delay, 0.1 * delay)
                    await asyncio.sleep(delay + jitter)
            if conn is None:
                logger.error("ApiKeyRepo: per-call connect failed: %s", last_err)
                raise last_err
            try:
                await conn.execute(
                    """
                    INSERT INTO api_keys (kid, name, owner, scopes, hashed_token, created_by)
                    VALUES ($1, $2, $3, $4::jsonb, $5, $6)
                    """,
                    kid,
                    name,
                    owner,
                    json.dumps(scopes),
                    hashed_token,
                    "system",
                )
            finally:
                await conn.close()
            return

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO api_keys (kid, name, owner, scopes, hashed_token, created_by)
                VALUES ($1, $2, $3, $4::jsonb, $5, $6)
                """,
                kid,
                name,
                owner,
                json.dumps(scopes),
                hashed_token,
                "system",
            )

    async def list_keys(self) -> List[dict]:
        if not self._pool:
            conn = await asyncpg.connect(self.dsn, ssl=False)
            try:
                rows = await conn.fetch(
                    "SELECT kid, name, owner, scopes, created_at, revoked_at FROM api_keys ORDER BY created_at"
                )
                return [dict(r) for r in rows]
            finally:
                await conn.close()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT kid, name, owner, scopes, created_at, revoked_at FROM api_keys ORDER BY created_at"
            )
            return [dict(r) for r in rows]

    async def revoke_key(self, kid: str) -> None:
        if not self._pool:
            conn = await asyncpg.connect(self.dsn, ssl=False)
            try:
                await conn.execute("UPDATE api_keys SET revoked_at = now() WHERE kid = $1", kid)
            finally:
                await conn.close()
            return

        async with self._pool.acquire() as conn:
            await conn.execute("UPDATE api_keys SET revoked_at = now() WHERE kid = $1", kid)
