## Hexagonal architecture enforcement (monolith-template)

This document describes the lightweight architectural rules enforced by the repository and how to run the enforcement checks locally.

Layer ordering (inner → outer)
- domain
- ports
- usecases
- services
- adapters (inbound/outbound)

Rules
- Outer layers must not import from inner layers (adapters → services → usecases → ports → domain).
- Exceptions require an ADR and Architect approval; document ADR number in the code comment where the exception is used.

Developer commands
- Run the AST-based architecture checker:

  ```bash
  python3 service-template/tools/arch_check.py
  ```

- Generate & validate OpenAPI (used by contract tests):

  ```bash
  python3 service-template/tools/generate_openapi.py
  python3 service-template/tools/validate_openapi.py service-template/src/app/openapi.json
  ```

- Run the policy test suite (fast):

  ```bash
  pytest -q monolith-template/tests/test_policies.py
  ```

How to propose an exception
- Create an ADR in `docs/adr/` (use template) describing why the exception is necessary.
- Add a code comment linking the ADR (e.g., `# ADR: 2025-001 - Reason`) where the import is allowed.
- Request Architect approval on the PR; CI will flag exceptions but will not block if an ADR reference is present (manual validation required).
