#!/usr/bin/env bash
set -euo pipefail

PORT=${PORT:-8000}
HOST=${HOST:-127.0.0.1}
BASE_URL="http://${HOST}:${PORT}"

SERVER_STARTED=0

cleanup() {
  if [ "$SERVER_STARTED" -eq 1 ] && [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# Check if server is already running
if ! curl -sf "${BASE_URL}/api/health" > /dev/null 2>&1; then
  echo "Starting API server on ${BASE_URL}..."
  .venv/bin/uvicorn api.main:app --host "$HOST" --port "$PORT" &
  SERVER_PID=$!
  SERVER_STARTED=1
  for _ in {1..30}; do
    if curl -sf "${BASE_URL}/api/health" > /dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
fi

echo "--- Testing /api/health ---"
curl -sf "${BASE_URL}/api/health" | grep -q '"status":"ok"'
echo "Health check passed."

echo "--- Testing Persona 1: SQL, Excel, Power BI, Tableau -> Data / BI Analyst ---"
RESP1=$(curl -sf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["sql", "excel", "power bi", "tableau"], "desired_role": "Data / BI Analyst"}')
echo "$RESP1" | grep -q '"role":"Data / BI Analyst"'
echo "Persona 1 passed."

echo "--- Testing Persona 2: Java, Spring Boot, MySQL, Docker -> Backend ---"
RESP2=$(curl -sf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["java", "spring boot", "mysql", "docker"], "desired_role": "Backend"}')
echo "$RESP2" | grep -q '"role":"Backend"'
echo "Persona 2 passed."

echo "--- Testing Persona 3: React, JavaScript, HTML, CSS -> Full Stack ---"
RESP3=$(curl -sf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["react", "javascript", "html", "css"], "desired_role": "Full Stack"}')
echo "$RESP3" | grep -q '"role":"Frontend"'
echo "Persona 3 passed."

echo "--- Testing Persona 4: Python, SQL, Pandas -> Data / BI Analyst (Known Limitation) ---"
RESP4=$(curl -sf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["python", "sql", "pandas"], "desired_role": "Data / BI Analyst"}')
echo "$RESP4" | grep -q '"role":"Backend"'
echo "Persona 4 passed."

echo "All smoke tests passed successfully."
