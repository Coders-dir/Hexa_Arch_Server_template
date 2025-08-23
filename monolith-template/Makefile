.PHONY: up down test build-image run

up:
	docker compose up --build -d

down:
	docker compose down

test:
	poetry run pytest -q

build-image:
	docker build -t ghcr.io/Coders-dir/hexa-monolith:local .

run:
	uvicorn src.app.main:app --reload
