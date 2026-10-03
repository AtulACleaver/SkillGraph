from fastapi.testclient import TestClient

from api.main import app, get_roles, get_skills

client = TestClient(app)


def test_get_roles():
    roles = get_roles()
    assert isinstance(roles, list)


def test_get_skills():
    skills = get_skills("python")
    assert isinstance(skills, list)


def test_post_gap_endpoint():
    response = client.post(
        "/gap",
        json={
            "skills": ["python", "fastapi"],
            "desired_role": "Backend",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_post_gap_endpoint_not_found():
    response = client.post(
        "/gap",
        json={
            "skills": ["python", "fastapi"],
            "desired_role": "Astronaut",
        },
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()
