.PHONY: up down test build-image run

.PHONY: arch-check lockfile-check bdd

up:
	docker compose up --build -d

down:
	docker compose down

test:
	poetry run pytest -q

arch-check:
	python tools/arch_check.py

lockfile-check:
	python tools/lockfile_check.py

bdd:
	poetry run pytest -q tests/features

build-image:
	docker build -t ghcr.io/Coders-dir/hexa-monolith:local .

run:
	uvicorn src.app.main:app --reload
