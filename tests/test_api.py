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
        assert isinstance(data, list)
        assert len(data) > 0
        assert "skill_id" in data[0]

def test_get_skills_empty():
    with TestClient(app) as client:
        response = client.get("/skills?q=nonexistent_skill_123")
        assert response.status_code == 200
        assert response.json() == []
