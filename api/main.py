import json
import os

from fastapi import FastAPI

from api.routes.gap import router as gap_router

app = FastAPI(
    title="SkillGraph API",
    description="India Job Market Mining Engine. Powers the frontend application with matching, readiness, and gap recommendation features.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Mining", "description": "Association rule mining and gap analysis"},
        {"name": "ML", "description": "Machine learning prediction and matching features"},
        {"name": "System", "description": "Health checks and vocabulary listings"},
    ]
)

app.include_router(gap_router)

# Use env var, default to fixtures
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "fixtures")

@app.get("/health", tags=["System"], summary="Health Check")
def health():
    return {
        "status": "ok"
    }

@app.get("/roles", tags=["System"], summary="List available role families")
def get_roles():
    roles_path = os.path.join(ARTIFACTS_DIR, "role_profiles.json")
    if not os.path.exists(roles_path):
        return []
    with open(roles_path, "r", encoding="utf-8") as f:
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

@app.get("/skills", tags=["System"], summary="Search skill vocabulary")
def get_skills(q: str = ""):
    vocab_path = os.path.join(ARTIFACTS_DIR, "skill_vocab.json")
    if not os.path.exists(vocab_path):
        return []
    with open(vocab_path, "r", encoding="utf-8") as f:
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
    return result[:20]