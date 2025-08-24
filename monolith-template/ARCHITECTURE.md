# Architecture (hexagonal) mapping for monolith-template

This file maps the repository layout to the hexagonal architecture (Ports & Adapters) pattern used by the template.

Layers and where to find them in this repo

- Domain (core business model): `src/app/domain/` — domain entities and pure business rules.
- Ports (interfaces): `src/app/ports/` — abstract repository interfaces and external service ports.
- Usecases / Application layer: `src/app/usecases/` — application orchestration that uses ports and domain.
- Application services: `src/app/services/` — thin wrappers used by controllers and wiring code.
- Adapters (inbound): `src/app/adapters/inbound/` — HTTP controllers, API routers, request validation.
- Adapters (outbound): `src/app/adapters/outbound/` — DB adapters (Mongo/Postgres), external HTTP clients (Supabase), in-memory adapters for tests.
- Infra: `src/app/infra/` — configuration, DB wiring, environment loading.

Example flow for "create user"

1. HTTP POST /api/users -> controller in `adapters/inbound/http/controllers/`.
2. Controller validates payload (Pydantic) and calls `services.UserService.create`.
3. `UserService.create` calls the usecase `create_user` in `usecases/`.
4. Usecase constructs a domain `User` and calls the `UserRepository` port to persist.
5. An outbound adapter (MongoUserRepo / PostgresUserRepo / InMemoryUserRepo) implements the `UserRepository` port and performs persistence.

Guidance
- Prefer small, focused usecases (single responsibility) and keep business rules inside domain models or domain services.
- Keep adapters thin and free of business logic. Tests should exercise usecases with in-memory adapters.
