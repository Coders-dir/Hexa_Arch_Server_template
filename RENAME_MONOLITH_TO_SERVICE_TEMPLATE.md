Rename plan
===========

This repository is moving `monolith-template/` to `service-template/` to better reflect multi-service support while enforcing hexagonal architecture.

Plan executed by automation:
1. Keep existing `monolith-template/` as-is for now (to preserve history).  
2. Create `service-template/` README and link to `monolith-template/` while the move completes.  
3. Future PR will move files and update imports.  

Notes
-----
Do not delete `monolith-template/` until all references are updated and CI passes.
