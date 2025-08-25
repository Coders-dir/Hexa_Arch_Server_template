# Changelog

## 2025-08-25 — CI & mypy fixes (merged from `fix/redis-quota-lint-mypy`)

- Fix: Redis quota adapter typing and runtime compatibility (safer imports, explicit types, queue score handling).
- Fix: `monolith-template/scripts/check_poetry_lock.py` tolerant of Poetry versions without `--check`.
- CI: Harden GitHub Actions workflows (install project deps before importing app, robust Docker/Compose handling, ensure app health for smoke tests).
- CI: Add caching for Poetry and pip in the monolith workflow to speed runs.
- Tests: Monolith test suite passes (17 passed, 1 skipped).

Notes
- Branch `fix/redis-quota-lint-mypy` has been merged into `main` and removed.
- Next recommended improvements: add repo-wide Poetry caching, remove deprecated `version:` from `docker-compose.test.yml`, and tighten mypy/ruff rules incrementally.
