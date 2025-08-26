# Migration plan: enforce hexagonal layout in `monolith-template`

This document describes a conservative, phased plan to reorganize `src/app` to a strict hexagonal layout and harden checks.

Phases
------
1. Safety-layer: add `tools/arch_check.py` (done) and unit tests. Run this on PRs.
2. Small refactors: add alias modules where duplicates exist (done for mongo_user_repo).
3. Physical reorg: move files into `domain`, `ports`, `usecases`, `services`, `adapters` incrementally in small PRs (< 10 files each) and update imports.
4. Enforce: enable stricter arch_check rules and add import-linter in CI.
5. Contract tests: expand `contracts/` and run strict contract checks in CI.

Rollback and safety
- Each physical move is accompanied by unit tests and arch_check run.
- Keep alias modules for one release cycle to preserve backwards compatibility.
