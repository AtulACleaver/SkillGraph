
from fastapi.testclient import TestClient

from api.main import app


def test_get_roles():
    with TestClient(app) as client:
        response = client.get("/api/roles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "role_family" in data[0]


def test_get_skills():
    with TestClient(app) as client:
        response = client.get("/api/skills?q=py")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "skill_id" in data[0]


def test_get_skills_empty():
    with TestClient(app) as client:
        response = client.get("/api/skills?q=nonexistent_skill_123")
        assert response.status_code == 200
        assert response.json() == []


def test_match():
    with TestClient(app) as client:
        response = client.post("/api/match", json={"skills": ["android", "kotlin", "java"]})
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) > 0
        assert data["matches"][0]["role"] == "Mobile"


def test_readiness():
    with TestClient(app) as client:
        response = client.post(
            "/api/readiness",
            json={"skills": ["react", "javascript", "typescript", "html", "css"], "desired_role": "Frontend"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["band"] == "Ready"


def test_readiness_unrecognized():
    with TestClient(app) as client:
        response = client.post("/api/readiness", json={"skills": ["asdfgh"], "desired_role": "Frontend"})
        assert response.status_code == 400


def test_gap():
    with TestClient(app) as client:
        response = client.post(
            "/api/gap",
            json={"skills": ["react", "javascript", "typescript", "html", "css"], "desired_role": "Frontend"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) == 5
        for rec in data["recommendations"]:
            assert rec["coverage_pct"] < 0.5
            assert rec["skill"] not in ["Frontend", "Front End"]


def test_gap_unknown_role():
    with TestClient(app) as client:
        response = client.post(
            "/api/gap",
            json={"skills": ["react"], "desired_role": "Astronaut"},
        )
        assert response.status_code == 400


def test_analyze():
    with TestClient(app) as client:
        response = client.post(
            "/api/analyze",
            json={"skills": ["react", "javascript", "typescript", "html", "css"], "desired_role": "Frontend"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["match"]["matches"]) > 0
        assert data["readiness"]["band"] == "Ready"
        assert len(data["gap"]["recommendations"]) == 5

