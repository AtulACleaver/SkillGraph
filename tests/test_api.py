import os

import pytest
from fastapi.testclient import TestClient

from api.main import app


def test_get_roles():
    with TestClient(app) as client:
        response = client.get("/roles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "role_family" in data[0]


def test_get_skills():
    with TestClient(app) as client:
        response = client.get("/skills?q=py")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "skill_id" in data[0]


def test_get_skills_empty():
    with TestClient(app) as client:
        response = client.get("/skills?q=nonexistent_skill_123")
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Fake fixtures cannot drive real model in CI")
def test_match():
    with TestClient(app) as client:
        response = client.post("/match", json={"skills": ["android", "kotlin", "java"]})
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) > 0
        assert data["matches"][0]["role"] == "Mobile"


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Fake fixtures cannot drive real model in CI")
def test_readiness():
    with TestClient(app) as client:
        response = client.post(
            "/readiness",
            json={"skills": ["react", "javascript", "typescript", "html", "css"], "desired_role": "Frontend"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["band"] == "Ready"


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Fake fixtures cannot drive real model in CI")
def test_readiness_unrecognized():
    with TestClient(app) as client:
        response = client.post("/readiness", json={"skills": ["asdfgh"], "desired_role": "Frontend"})
        assert response.status_code == 400
