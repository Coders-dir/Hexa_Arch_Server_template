Microservices Hexagonal Template (FastAPI)

Overview
This is a production-ready template for a Microservice-per-Hexagon layout using FastAPI. Each service follows the same hexagonal structure and can be built and deployed independently.

Highlights
- Services in `services/` folder, each a full FastAPI hexagonal service
- Shared infra for CI and k8s charts
- GitHub Actions matrix-based CI for services

Quick start (local)
1. cd services/user-service
2. Copy `.env.example` to `.env` and fill values
3. docker compose up --build

Required GitHub secrets (per service)
- DATABASE_URL_STAGING, DATABASE_URL_PROD, DB_MIGRATION_URL
- JWT_SECRET
- DOCKER_REGISTRY / DOCKER_REGISTRY_PASSWORD
- KUBE_CONFIG (for deployments)

