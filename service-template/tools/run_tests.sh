#!/usr/bin/env bash
set -euo pipefail

# Small helper to run enforcement tests and OpenAPI generation locally in a reproducible way.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT"

echo "Running direct policy pytest wrappers..."
python -m pytest -q "$ROOT/tests/test_api_contracts_pytest.py" \
  "$ROOT/tests/test_architecture_pytest.py" \
  "$ROOT/tests/test_lockfile_pytest.py"

echo "Generating OpenAPI..."
python "$ROOT/tools/generate_openapi.py"

echo "Running contract check..."
python "$ROOT/tools/contract_check.py"

echo "All policy checks completed successfully."
