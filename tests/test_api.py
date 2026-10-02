from api.main import get_roles, get_skills


def test_get_roles():
    roles = get_roles()
    assert isinstance(roles, list)

def test_get_skills():
    skills = get_skills("python")
    assert isinstance(skills, list)
