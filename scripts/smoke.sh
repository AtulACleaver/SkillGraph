#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
BASE_URL="${BASE_URL%/}"

SERVER_STARTED=0
cleanup() {
  if [ "$SERVER_STARTED" -eq 1 ] && [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# Auto-start local uvicorn if target is localhost and not reachable
if [[ "${BASE_URL}" == *"127.0.0.1"* || "${BASE_URL}" == *"localhost"* ]]; then
  if ! curl -sf "${BASE_URL}/api/health" > /dev/null 2>&1; then
    PORT="${BASE_URL##*:}"
    PORT="${PORT%%/*}"
    echo "Starting local API server on ${BASE_URL}..."
    .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port "${PORT:-8000}" &
    SERVER_PID=$!
    SERVER_STARTED=1
    for _ in {1..30}; do
      if curl -sf "${BASE_URL}/api/health" > /dev/null 2>&1; then
        break
      fi
      sleep 0.2
    done
  fi
fi

echo "Running smoke tests against: ${BASE_URL}"

# 1. Health check
echo "1. Checking GET /api/health..."
HEALTH=$(curl -sSf "${BASE_URL}/api/health")
echo "${HEALTH}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
assert data.get("status") == "ok", f"Invalid status: {data}"
assert data.get("artifacts_loaded") is True, "artifacts_loaded is not True"
print("   Passed: status ok, artifacts_loaded true")
'

# 2. Roles list check
echo "2. Checking GET /api/roles returns 10 roles..."
ROLES=$(curl -sSf "${BASE_URL}/api/roles")
echo "${ROLES}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
assert isinstance(data, list), "Roles response is not a list"
assert len(data) == 10, f"Expected 10 roles, got {len(data)}"
print(f"   Passed: exactly {len(data)} roles returned")
'

# 3. Skills autocomplete check
echo "3. Checking GET /api/skills?q=pyth is non-empty..."
SKILLS=$(curl -sSf "${BASE_URL}/api/skills?q=pyth")
echo "${SKILLS}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
assert isinstance(data, list), "Skills response is not a list"
assert len(data) > 0, "Skills response is empty"
assert any("python" in s.get("name", "").lower() for s in data), "Expected Python in suggestions"
print(f"   Passed: {len(data)} skills returned")
'

# 4. Persona 1 check (sql, excel, power bi, tableau -> Data / BI Analyst)
echo "4. Checking Persona 1 (sql, excel, power bi, tableau -> Data / BI Analyst)..."
P1=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"skills\":[\"sql\",\"excel\",\"power bi\",\"tableau\"],\"desired_role\":\"Data / BI Analyst\"}")
echo "${P1}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
match = data.get("match", {})
top_match = match.get("matches", [{}])[0]
role = top_match.get("role")
assert role == "Data / BI Analyst", f"Expected Data / BI Analyst, got {role}"
prob = round(top_match.get("probability", 0), 4)
assert prob == 0.9733, f"Expected match prob 0.9733, got {prob}"

readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.9733, f"Expected readiness prob 0.9733, got {r_prob}"
band = readiness.get("band")
assert band == "Close", f"Expected band Close, got {band}"
cov = round(readiness.get("coverage", 0), 2)
assert cov == 0.1, f"Expected coverage 0.1, got {cov}"
print("   Passed: Persona 1 match 0.9733, readiness 0.9733, band Close, coverage 0.1")
'

# 5. Persona 2 check (java, spring boot, mysql, docker -> Backend)
echo "5. Checking Persona 2 (java, spring boot, mysql, docker -> Backend)..."
P2=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"skills\":[\"java\",\"spring boot\",\"mysql\",\"docker\"],\"desired_role\":\"Backend\"}")
echo "${P2}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.7520, f"Expected readiness prob 0.7520, got {r_prob}"
band = readiness.get("band")
assert band == "Close", f"Expected band Close, got {band}"
cov = round(readiness.get("coverage", 0), 2)
assert cov == 0.15, f"Expected coverage 0.15, got {cov}"
print("   Passed: Persona 2 readiness 0.7520, band Close, coverage 0.15")
'

# 6. Persona 3 check (react, javascript, html, css -> Full Stack)
echo "6. Checking Persona 3 (react, javascript, html, css -> Full Stack)..."
P3=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"skills\":[\"react\",\"javascript\",\"html\",\"css\"],\"desired_role\":\"Full Stack\"}")
echo "${P3}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
match = data.get("match", {})
top_match = match.get("matches", [{}])[0]
role = top_match.get("role")
assert role == "Frontend", f"Expected Frontend, got {role}"
prob = round(top_match.get("probability", 0), 4)
assert prob == 0.7369, f"Expected match prob 0.7369, got {prob}"

readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.2395, f"Expected readiness prob 0.2395, got {r_prob}"
band = readiness.get("band")
assert band == "Not yet", f"Expected band Not yet, got {band}"
print("   Passed: Persona 3 match Frontend 0.7369, readiness 0.2395, band Not yet")
'

# 7. Persona 4 check (python, sql, pandas -> Data / BI Analyst, known limitation)
echo "7. Checking Persona 4 (python, sql, pandas -> Data / BI Analyst, known limitation)..."
P4=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"skills\":[\"python\",\"sql\",\"pandas\"],\"desired_role\":\"Data / BI Analyst\"}")
echo "${P4}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
match = data.get("match", {})
top_match = match.get("matches", [{}])[0]
role = top_match.get("role")
assert role == "Backend", f"Expected Backend, got {role}"
prob = round(top_match.get("probability", 0), 4)
assert prob == 0.4906, f"Expected match prob 0.4906, got {prob}"

readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.1080, f"Expected readiness prob 0.1080, got {r_prob}"
band = readiness.get("band")
assert band == "Not yet", f"Expected band Not yet, got {band}"
print("   Passed: Persona 4 match Backend 0.4906, readiness 0.1080, band Not yet")
'

# 8. Unrecognized skills 400 check
echo "8. Checking unrecognized skills returns 400..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"skills\":[\"foo\",\"bar\"],\"desired_role\":\"Data / BI Analyst\"}")
if [ "${HTTP_STATUS}" -ne 400 ]; then
  echo "   Failed: Expected HTTP 400 for unrecognized skills, got ${HTTP_STATUS}"
  exit 1
fi
echo "   Passed: HTTP 400 returned for unrecognized skills"

echo "All smoke tests passed successfully against ${BASE_URL}."
