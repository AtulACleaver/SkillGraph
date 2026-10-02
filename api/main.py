import json
import os

from fastapi import FastAPI

app = FastAPI(
    title="SkillGraph API",
    version="0.1.0"
)

# Use env var, default to fixtures
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "fixtures")

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/roles")
def get_roles():
    roles_path = os.path.join(ARTIFACTS_DIR, "role_profiles.json")
    if not os.path.exists(roles_path):
        return []
    with open(roles_path, "r") as f:
        data = json.load(f)
    
    # Expected: [{role_family, n_postings, top_skills: [...]}]
    result = []
    for role, details in data.items():
        result.append({
            "role_family": role,
            "n_postings": details.get("n_postings", 0),
            "top_skills": details.get("top_skills", [])
        })
    return result

@app.get("/skills")
def get_skills(q: str = ""):
    vocab_path = os.path.join(ARTIFACTS_DIR, "skill_vocab.json")
    if not os.path.exists(vocab_path):
        return []
    with open(vocab_path, "r") as f:
        data = json.load(f)
    
    # Expected: [{skill_id, name, aliases: [...]}]
    result = []
    q_lower = q.lower()
    for name, skill_id in data.items():
        if q_lower in name:
            result.append({
                "skill_id": skill_id,
                "name": name.title(),
                "aliases": []
            })
    # Day 4 requires capping at 20 results, but for Day 2 it's fine. We'll cap at 20.
    return result[:20]