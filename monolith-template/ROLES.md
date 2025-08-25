# Roles and Responsibilities (monolith-template)

This document enumerates the primary roles the template recognizes and the responsibilities each role must satisfy.
Roles are intentionally opinionated to keep the template coherent. Projects can extend these roles, but must
adhere to the core policies described in `REQUIREMENTS_BDD.md`.

Primary roles
-------------

1. Architecte Hexagonal
   - Owner: architecture and layering rules.
   - Responsibilities:
     - Maintain `ARCHITECTURE.md` and architecture tests.
     - Approve exceptions (ADR required).
   - Artefacts: `ARCHITECTURE.md`, `tools/arch_check.py` results.

2. API Owner
   - Owner: OpenAPI & HTTP contract.
   - Responsibilities:
     - Maintain OpenAPI spec, API changelog.
     - Approve breaking API changes.
   - Artefacts: OpenAPI JSON, API changelog, contract tests.

3. DevOps / Platform
   - Owner: CI/CD, secrets, runbooks.
   - Responsibilities:
     - Ensure reproducible builds (`poetry.lock`).
     - Maintain `RUNBOOK.md`, CI workflows, k8s overlays.
   - Artefacts: `RUNBOOK.md`, CI workflows, `infra/` manifests.

4. Domain / Product Owner
   - Owner: domain models and business invariants.
   - Responsibilities:
     - Define domain entities, invariants and acceptance tests.
   - Artefacts: domain spec, domain test-suite.

5. QA / Test Owner
   - Owner: test strategy and BDD scenarios.
   - Responsibilities:
     - Maintain `features/` structure for the template policies.
     - Ensure tests run in CI and are reliable.
   - Artefacts: `features/`, test-matrix, flaky-test policy.

6. Security / Compliance
   - Owner: secrets and compliance checks.
   - Responsibilities:
     - Enforce secrets policy, dependency scanning, RBAC minimal policy.
   - Artefacts: `SECURITY.md`, SOPS/Vault guidance.

7. Release Manager
   - Owner: template releases and upgrade notes.
   - Responsibilities:
     - Tagging releases, migration notes, changelogs.

Governance
----------
- Code changes that affect layering, contracts, or infra require approval from the relevant role.
- Exceptions must be captured with an ADR and approved by the Architect.
