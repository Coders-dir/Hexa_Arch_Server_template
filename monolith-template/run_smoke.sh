#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Starting monolith smoke run..."
docker compose up --build -d
sleep 6
echo -n "Checking /health... "
curl -fsS http://127.0.0.1:8000/health && echo "OK"
echo -n "Checking create user... "
curl -fsS -X POST http://127.0.0.1:8000/api/users/ -H 'Content-Type: application/json' -d '{"email":"smoke@example.com","name":"Smoke"}' && echo "OK"
echo "Tearing down..."
docker compose down
echo "Monolith smoke run completed."
