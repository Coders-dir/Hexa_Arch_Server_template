from pathlib import Path
import sys

# Add repo src to path for tests (must happen before importing test modules that use `src`)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402

import pytest  # noqa: E402


def _run_compose_up(compose_file: str):
    cmd = ["docker-compose", "-f", compose_file, "up", "-d"]
    subprocess.check_call(cmd)


def _run_compose_down(compose_file: str):
    cmd = ["docker-compose", "-f", compose_file, "down", "-v"]
    subprocess.check_call(cmd)


def _wait_for_port(host: str, port: int, timeout: int = 30):
    import socket

    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def integration_dbs():
    """Optional fixture that starts local Postgres and Mongo services using docker-compose.

    To enable, run tests with the environment variable `RUN_INTEGRATION=1`.
    The fixture sets environment variables `DATABASE_URL` and `MONGO_URI` for tests.
    """
    run_integration = os.getenv("RUN_INTEGRATION") == "1"
    compose_file = os.path.join(os.path.dirname(__file__), "..", "docker-compose.test.yml")

    if not run_integration:
        yield None
        return

    # Start docker-compose
    try:
        _run_compose_up(compose_file)
    except Exception as e:
        pytest.skip(f"Could not start docker-compose test services: {e}")

    # Wait for Postgres
    if not _wait_for_port("127.0.0.1", 5432, timeout=60):
        _run_compose_down(compose_file)
        pytest.skip("Postgres did not become ready in time")

    # Apply DB migrations (simple approach: pipe local SQL into the Postgres container)
    try:
        migrations_dir = os.path.join(os.path.dirname(__file__), "..", "db", "migrations")
        migration_file = os.path.join(migrations_dir, "001_create_api_keys.sql")
        if os.path.exists(migration_file):
            cmd = f"cat {migration_file} | docker exec -i monolith-template-postgres-1 psql -U test -d test_db"
            subprocess.check_call(cmd, shell=True)
    except Exception as e:
        _run_compose_down(compose_file)
        pytest.skip(f"Could not apply migrations: {e}")

    # Wait for Mongo
    if not _wait_for_port("127.0.0.1", 27017, timeout=60):
        _run_compose_down(compose_file)
        pytest.skip("Mongo did not become ready in time")

    # Export env vars for tests
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@127.0.0.1:5432/test_db")
    os.environ.setdefault("MONGO_URI", "mongodb://127.0.0.1:27017/test_db")

    yield {
        "DATABASE_URL": os.environ["DATABASE_URL"],
        "MONGO_URI": os.environ["MONGO_URI"],
    }

    # Teardown
    _run_compose_down(compose_file)
