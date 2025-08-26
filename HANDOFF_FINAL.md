Final handoff — consolidation to single `main`

What I did
- Migrated canonical template to `service-template/` and updated references across docs and workflows.
- Removed legacy folders: `monolith-template/` and `microservices-template/` from the repository.
- Updated CI workflows and `service-template/Dockerfile` to be robust in GitHub Actions environments.
- Cleaned tracked Python bytecode and added `.gitignore` entries.
- Ran non-integration tests locally: 20 passed, 4 skipped.
- Pruned remote branches; verified only `main` branch remains.

Remaining items (requires org/repo admin or account changes)
- Branch protection: API attempt failed with 403 due to repository plan limits (private repo without required features). Please enable branch protection via the GitHub UI or upgrade plan.
- CODEOWNERS: I updated the placeholder file but you should replace `@Coders-dir/*` team placeholders with real org teams and confirm.
- SCA/SBOM secrets and protected checks: needs organization secrets and SCA tooling enabled.

How to verify
1. Run GitHub Actions on `main` and confirm all workflows are green.
2. Validate protected branch settings in repo settings -> Branches.
3. Confirm `.github/CODEOWNERS` lines map to actual GitHub teams.

If you want me to continue with automated merges or branch protection after plan/permission changes, supply updated credentials or make the necessary plan/permission updates and I'll finish remaining items.

Signed off by: CTO (automation)
