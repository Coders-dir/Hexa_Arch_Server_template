tests README

This folder contains unit and integration tests for the monolith template.

Fake Redis
----------
`tests/fake_redis.py` provides a lightweight in-memory emulation used for local test runs to avoid requiring a real Redis instance.

Currently emulated commands and behaviors:
- `get`, `set(ex=)`, `delete`, `incr`, `expire`
- Sorted-set helpers: `zadd`, `zrange`, `zpopmin` (and a helper `zrangebyscore` used internally)
- Minimal `eval` emulation for the specific Lua script used by `QuotaManager.pop_queue_priority` (ZRANGEBYSCORE + ZREM semantics)
- Expiry handling: keys set with `ex` or via `expire` are removed after the expiry timestamp
- Async wrappers (`FakeAsyncRedis`) matching `redis.asyncio` methods used in tests

Limitations:
- This fake only implements the subset of Redis commands required by tests. Do not rely on it as a complete Redis substitute.
- `eval` is a minimal emulation targeted at the library's use-case; arbitrary Lua scripts are not supported.

Running tests locally
---------------------
Preferred quick-run that sets PYTHONPATH and runs tests in this folder:

```bash
export PYTHONPATH=$(pwd)/monolith-template
python -m pytest monolith-template/tests -q
```

There's also a helper script provided in `monolith-template/tools/run_tests.sh` which sets up the environment and runs enforcement checks.

Integration / full tests
------------------------
Some tests require external services (Redis, Postgres, Mongo). By default heavy integration tests are skipped. To run them locally you can enable the environment variable:

```bash
export RUN_FULL_TESTS=1
python -m pytest monolith-template/tests -q
```

If you prefer to run real services, start Redis on `127.0.0.1:6379` before enabling `RUN_FULL_TESTS`.

Contact
-------
If you need additional Redis commands emulated, open a ticket or add them to `tests/fake_redis.py` with test coverage demonstrating the new behavior.
