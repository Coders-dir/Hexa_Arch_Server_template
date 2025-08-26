# Requirements as BDD policies (template-level)

This file defines the template-level requirements expressed as Behavior-Driven Development (BDD) policies.
These policies codify roles, responsibilities and non-negotiable rules the template enforces. They are intentionally
opinionated: the template owns these policies to keep projects consistent, maintainable and testable.

Scope
-----
- Applies only to `monolith-template/` (the template) and projects bootstrapped from it.
- Runs in GitHub Codespaces and CI. Heavy integration policies run in a gated CI job.

How to use
----------
- Policies are written as abstract Gherkin scenarios and mapped to test steps (see `features/`).
- Fast, static policies run in PR checks (arch check, lockfile check). Integration policies run in an integration stage.

Core principle (non-negotiable)
--------------------------------
"All code dependencies must point inwards: adapters -> ports -> usecases/services -> domain. No outward imports allowed."

Primary roles and responsibilities
---------------------------------
- See `ROLES.md` for the canonical list of roles, owners and artefacts.

Policy categories
-----------------
- Architecture enforcement (static import checks)
- API ownership & contract tests (OpenAPI generation, contract verification)
- DevOps & reproducible builds (lockfile checks, reproducible CI)
- Security (secrets policy, RBAC minimal defaults)

Features & examples
--------------------
See `features/` for example Gherkin policies. These are abstract and map to simple enforcement steps.

Enforcement & CI
-----------------
- `ci/ci-bdd.yml` runs the quick policies (arch_check). Integration features run in a separate integration job.
- PRs that touch critical layers require the appropriate role approval (managed by CODEOWNERS / branch rules).

Next steps
----------
- Expand `features/` with team-specific domain policies.
- Add contract tests and lightweight mocking for faster PR feedback.

Contact & governance
--------------------
Architectural exceptions must create an ADR and be approved by the Architect role. See `ROLES.md`.
