Rename plan
===========

This repository has consolidated `monolith-template/` into `service-template/` to better reflect multi-service support while enforcing hexagonal architecture.

Plan executed:
1. Files and documentation were migrated to `service-template/`.
2. CI and workflow references were updated to use `service-template/`.
3. Historical migration helpers and notes are archived under `tools/archive/`.

Notes
-----
`monolith-template` has been removed from the active tree. If you need the historical layout, consult `tools/archive/` and `HANDOFF_SUMMARY.md`.
