PROJECT CONTEXT
===============

Purpose
-------
This repository provides a hexagonal server template for building services with a spec-first, AI-assisted development workflow.

Quick orientation
-----------------
- Canonical template folder: `service-template/` (contains hexagonal layout).  
- Roles and requirements: `service-template/roles/` (machine-readable YAML and human docs).  
- Executable specs (BDD): `service-template/features/`  
- Requirements manifest (traceability): `requirements-manifest.json`  
- AI session context: `ai_context.json` (used by AI agents to find entry points)  
- Prompt counter: `PROMPT_COUNTER.md` + `tools/increment_prompt_counter.py`

Codespaces note
---------------
All work is expected to run inside GitHub Codespaces. Heavy integration tests or cluster operations may require additional permissions or remote runners; see `service-template/DEV_ONBOARDING.md` for options. Keep local iteration fast and use CI for integration runs.

Important constraints
---------------------
- Hexagonal architecture is required. Do not introduce alternative project structures.  
- Requirement-first workflow: all new features start as a role requirement with acceptance criteria (Gherkin).  
- Sensitive changes (auth, secrets, infra, billing, PII) require role owner approval (see `CODEOWNERS`).

How AI sessions should start
---------------------------
1. Read `PROJECT_CONTEXT.md`.  
2. Read `ai_context.json` to find the canonical entry points and roles.  
3. Read `PROMPT_COUNTER.md` and call `tools/increment_prompt_counter.py` to record a new session.  

Where to get help
-----------------
See `ROLES.md` and the role YAMLs under `service-template/roles/` for owners and responsibilities.

Migration note
--------------
The repository migration from `monolith-template/` into `service-template/` is complete. Historical migration helpers are archived in `tools/archive/` and `HANDOFF_SUMMARY.md` contains a changelog of the steps performed.
