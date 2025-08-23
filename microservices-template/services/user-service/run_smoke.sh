#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Starting user-service smoke run..."
docker compose up --build -d
sleep 6
echo "Checking /health..."
curl -fsS http://127.0.0.1:8001/health && echo " OK"
echo "Checking user route..."
curl -fsS http://127.0.0.1:8001/api/users/abc && echo " OK"
echo "Tearing down..."
docker compose down
echo "User-service smoke run completed."
