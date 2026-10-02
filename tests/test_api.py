from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

def test_get_roles():
    response = client.get("/roles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "role_family" in data[0]

def test_get_skills():
    response = client.get("/skills?q=py")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "skill_id" in data[0]

def test_get_skills_empty():
    response = client.get("/skills?q=nonexistent_skill_123")
    assert response.status_code == 200
    assert response.json() == []
