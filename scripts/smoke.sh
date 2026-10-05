#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://skillgraph-two-delta.vercel.app}"
BASE_URL="${BASE_URL%/}"

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

# 4. Persona 1 check
echo "4. Checking Persona 1 (python, sql, pandas -> Data / BI Analyst)..."
P1=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills":["python","sql","pandas"],"desired_role":"Data / BI Analyst"}')
echo "${P1}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
match = data.get("match", {})
top_match = match.get("matches", [{}])[0]
role = top_match.get("role")
assert role == "Data / BI Analyst", f"Expected Data / BI Analyst, got {role}"
prob = round(top_match.get("probability", 0), 4)
assert prob == 0.4313, f"Expected match prob 0.4313, got {prob}"

readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.4313, f"Expected readiness prob 0.4313, got {r_prob}"
band = readiness.get("band")
assert band == "Close", f"Expected band Close, got {band}"
cov = round(readiness.get("coverage", 0), 2)
assert cov == 0.1, f"Expected coverage 0.1, got {cov}"
print("   Passed: Persona 1 match 0.4313, readiness 0.4313, band Close, coverage 0.1")
'

# 5. Persona 2 check
echo "5. Checking Persona 2 (java, spring boot, mysql, docker -> Backend)..."
P2=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills":["java","spring boot","mysql","docker"],"desired_role":"Backend"}')
echo "${P2}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.6942, f"Expected readiness prob 0.6942, got {r_prob}"
band = readiness.get("band")
assert band == "Close", f"Expected band Close, got {band}"
cov = round(readiness.get("coverage", 0), 2)
assert cov == 0.15, f"Expected coverage 0.15, got {cov}"
print("   Passed: Persona 2 readiness 0.6942, band Close, coverage 0.15")
'

# 6. Persona 3 check
echo "6. Checking Persona 3 (react, javascript, html, css -> Full Stack)..."
P3=$(curl -sSf -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills":["react","javascript","html","css"],"desired_role":"Full Stack"}')
echo "${P3}" | python3 -c '
import sys, json
data = json.load(sys.stdin)
match = data.get("match", {})
top_match = match.get("matches", [{}])[0]
role = top_match.get("role")
assert role == "Frontend", f"Expected Frontend, got {role}"
prob = round(top_match.get("probability", 0), 4)
assert prob == 0.7072, f"Expected match prob 0.7072, got {prob}"

readiness = data.get("readiness", {})
r_prob = round(readiness.get("probability", 0), 4)
assert r_prob == 0.2588, f"Expected readiness prob 0.2588, got {r_prob}"
band = readiness.get("band")
assert band == "Not yet", f"Expected band Not yet, got {band}"
print("   Passed: Persona 3 match Frontend 0.7072, readiness 0.2588, band Not yet")
'

# 7. Unrecognized skills 400 check
echo "7. Checking unrecognized skills returns 400..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills":["foo","bar"],"desired_role":"Data / BI Analyst"}')
if [ "${HTTP_STATUS}" -ne 400 ]; then
  echo "   Failed: Expected HTTP 400 for unrecognized skills, got ${HTTP_STATUS}"
  exit 1
fi
echo "   Passed: HTTP 400 returned for unrecognized skills"

echo "All smoke tests passed successfully against ${BASE_URL}."
