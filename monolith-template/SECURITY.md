# SECURITY

This is a template repository. Follow these minimal security guidelines:

- Never commit production secrets (DB passwords, API keys, service account tokens) into the repo.
- Use environment variables (`.env` or CI secrets) to provide credentials. Example `.env.example` is provided.
- Rotate the `cd-deployer` kubeconfig and GitHub secrets regularly.
- Use least-privilege RBAC: the included `infra/k8s/cd-deployer-role.yaml` is namespaced for `prod` and intended for CI/CD only.
- Validate and sanitize all inbound input. Use Pydantic models for request validation in controllers.
- Add dependency scanning and secret scanning to CI (Dependabot, Snyk, GitHub secret scanning).

If you need help setting up secure CI secret injection or secret rotation, consult your platform security team.
