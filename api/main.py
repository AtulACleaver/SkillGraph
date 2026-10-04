import logging
import time
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api import schemas
from api.artifacts import artifacts
from etl.normalize import skills_to_vector
from ml import predict as ml_predict

cached_roles: list[schemas.RoleResponse] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    artifacts.load()
    
    # Cache roles at startup
    cached_roles.clear()
    for role, details in artifacts.role_profiles.items():
        cached_roles.append(schemas.RoleResponse(
            role_family=role,
            n_postings=details.get("n_postings", 0),
            top_skills=details.get("top_skills", [])
        ))
        
    yield

app = FastAPI(
    title="SkillGraph API",
    version="0.1.0",
    lifespan=lifespan
)

@app.middleware("http")
async def add_process_time_and_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {process_time*1000:.2f}ms")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    logger.error(f"[{request_id}] Unhandled exception at {request.method} {request.url.path}: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "request_id": request_id}
    )

# CORS Middleware (Local dev origin for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_valid_roles() -> list[str]:
    return list(artifacts.role_profiles.keys())

def validate_request(skills: list[str], desired_role: str | None = None):
    if not skills:
        raise HTTPException(status_code=400, detail="skills list cannot be empty")
    if desired_role is not None:
        valid_roles = get_valid_roles()
        if valid_roles and desired_role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Unknown role. Valid roles are: {valid_roles}")


@app.get("/health", response_model=schemas.HealthResponse)
def health():
    return schemas.HealthResponse(
        status="ok",
        artifacts_loaded=artifacts.artifacts_loaded,
        n_postings=artifacts.n_postings,
        n_skills=artifacts.n_skills,
        built_at="2026-10-02T00:00:00Z"
    )

@app.get("/roles", response_model=list[schemas.RoleResponse])
def get_roles():
    return cached_roles

@app.get("/skills", response_model=list[schemas.SkillResponse])
def get_skills(q: str = ""):
    result = []
    q_lower = q.lower()
    for item in artifacts.autocomplete:
        names = [item["name"], item["display"], *item.get("aliases", [])]
        if any(q_lower in n.lower() for n in names):
            result.append(schemas.SkillResponse(
                skill_id=item["id"],
                name=item["display"],
                aliases=item.get("aliases", [])
            ))
            if len(result) == 20:
                break
    return result

def _to_vector(skills: list[str]):
    vector, unrecognized = skills_to_vector(skills)
    if not vector.any():
        raise HTTPException(status_code=400, detail={"message": "None of these skills are recognized", "unrecognized": unrecognized})
    return vector, unrecognized

@app.post("/match", response_model=schemas.MatchResponse)
def match(request: schemas.MatchRequest):
    validate_request(request.skills)
    vector, unrecognized = _to_vector(request.skills)
    top = ml_predict.predict_roles(vector)[:3]
    return schemas.MatchResponse(matches=[schemas.MatchDetail(**m) for m in top], unrecognized=unrecognized)

@app.post("/readiness", response_model=schemas.ReadinessResponse)
def readiness(request: schemas.ReadinessRequest):
    validate_request(request.skills, request.desired_role)
    vector, _ = _to_vector(request.skills)
    try:
        result = ml_predict.readiness(vector, request.desired_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ReadinessResponse(**result)

@app.post("/gap", response_model=schemas.GapResponse)
def gap(request: schemas.GapRequest):
    validate_request(request.skills, request.desired_role)
    return schemas.GapResponse(
        recommendations=[
            schemas.GapRecommendation(
                skill="sql",
                coverage_pct=0.8,
                readiness_gain=0.15,
                learn_with=[]
            )
        ]
    )

@lru_cache(maxsize=500)
def _analyze_cached(skills_tuple: tuple[str, ...], desired_role: str | None) -> schemas.AnalyzeResponse:
    skills = list(skills_tuple)
    match_resp = match(schemas.MatchRequest(skills=skills))
    read_resp = readiness(schemas.ReadinessRequest(skills=skills, desired_role=desired_role))
    gap_resp = gap(schemas.GapRequest(skills=skills, desired_role=desired_role))
    
    return schemas.AnalyzeResponse(
        match=match_resp,
        readiness=read_resp,
        gap=gap_resp
    )

@app.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze(request: schemas.AnalyzeRequest):
    validate_request(request.skills, request.desired_role)
    
    skills_tuple = tuple(sorted(request.skills))
    return _analyze_cached(skills_tuple, request.desired_role)