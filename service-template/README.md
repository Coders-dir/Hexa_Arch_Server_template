Service Template (hexagonal)
===========================

This folder contains the hexagonal server template. It was formerly named `monolith-template` but is intended to be reused for single-service or monolith-style projects that follow hexagonal architecture.

Quick start (Codespaces-friendly)
--------------------------------
1. Open in GitHub Codespaces.  
2. Read the top-level `PROJECT_CONTEXT.md` for vision and roles.  
3. Run unit tests with `poetry run pytest` inside `service-template` if you have Poetry installed. Heavy integration requires remote CI or a developer machine with Docker.

Architecture mandate
--------------------
All code in this folder follows hexagonal architecture: adapters (inbound/outbound), ports, usecases/services, domain. Any divergence requires an ADR and Architect signoff.

Migration note
--------------
The full template contents currently live in `monolith-template/`. A future PR will migrate and reconcile files into this folder; for now use `monolith-template/` as the canonical source for template contents.
