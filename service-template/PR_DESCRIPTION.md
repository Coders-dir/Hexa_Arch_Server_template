Title: refactor: organize adapters and inbound controllers into clear packages

Summary
-------
This PR reorganizes the monolith template to enforce a clearer hexagonal layout and adds policy checks to prevent regressions.

Key changes
-----------
- Reorganized outbound adapters into explicit packages:
  - `src/app/adapters/outbound/db/` (Postgres, Mongo, ApiKey, InMemory)
  - `src/app/adapters/outbound/external/` (Supabase client)
  - `src/app/adapters/outbound/cache/` (Redis quota, redis scripts)
- Reorganized inbound HTTP controllers into domain folders:
  - `src/app/adapters/inbound/http/controllers/users/`
  - `src/app/adapters/inbound/http/controllers/admin/`
- Added thin re-export stubs at the original paths to preserve compatibility.
- Added policy enforcement tooling and tests:
  - `monolith-template/tools/arch_check.py` (AST-based import direction enforcement)
  - `monolith-template/tools/generate_openapi.py`, `validate_openapi.py`, `contract_check.py`
  - `monolith-template/tests/test_policies.py` and pytest-bdd step stubs
- Generated baseline OpenAPI contract at `monolith-template/contracts/expected_openapi.json`.

Why
---
The goal is to make the monolith template more opinionated and maintainable by grouping adapters by concern (db, external, cache) and making inbound controllers domain-centric. The changes are incremental and preserve backwards-compatible import paths via re-exports.

How to review
-------------
1. Checkout the branch `refactor/organize-adapters` (already created).
2. Run the policy checks locally:

   ```bash
   python3 monolith-template/tools/arch_check.py
   pytest -q monolith-template/tests/test_policies.py
   ```

3. Verify that existing public imports still resolve (the repo includes thin re-export stubs to preserve compatibility).
4. Review moved modules for API surface changes (especially adapter init signatures).

Suggested reviewers / roles
--------------------------
- Architect (architecture and import-direction sign-off)
- API Owner (OpenAPI/contract changes)
- DevOps (lockfile & CI checks)
- Domain owner for `users` (behavioral expectations of moved controllers)

Notes for merging
-----------------
- The PR includes CI workflows that will run policy checks; ensure GitHub Actions pass before merging.
- If the OpenAPI contract changes are intentional, update `monolith-template/contracts/expected_openapi.json` and add an explicit note in the PR body explaining the consumer-facing change.

How I validated
----------------
- Ran AST architecture checker and policy test suite in this Codespace; all checks passed.

Next steps after merge
----------------------
- Continue moving remaining modules in small batches and run the `arch_check` after each batch.
- Expand the pytest-bdd scenarios to cover ADR approvals and API-owner gating for contract changes.

Copy-paste PR body
------------------
Use the contents of this file as the PR description when you open the pull request on GitHub.
