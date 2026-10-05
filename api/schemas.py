
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    artifacts_loaded: bool = False
    n_postings: int = 0
    n_skills: int = 0
    built_at: str | None = None
    model: str | None = None
    rules: str | None = None

class RoleResponse(BaseModel):
    role_family: str
    n_postings: int
    top_skills: list[str]

class SkillResponse(BaseModel):
    skill_id: int
    name: str
    aliases: list[str] = Field(default_factory=list)

class MatchRequest(BaseModel):
    skills: list[str]

class MatchDetail(BaseModel):
    role: str
    probability: float

class MatchResponse(BaseModel):
    matches: list[MatchDetail]
    unrecognized: list[str] = Field(default_factory=list)

class ReadinessRequest(BaseModel):
    skills: list[str]
    desired_role: str

class ReadinessResponse(BaseModel):
    probability: float
    band: str
    coverage: float
    covered: list[str]
    missing_count: int

class GapRequest(BaseModel):
    skills: list[str]
    desired_role: str

class GapRecommendation(BaseModel):
    skill: str
    coverage_pct: float
    readiness_gain: float
    learn_with: list[str] = Field(default_factory=list)

class GapResponse(BaseModel):
    recommendations: list[GapRecommendation]

class AnalyzeRequest(BaseModel):
    skills: list[str]
    desired_role: str

class AnalyzeResponse(BaseModel):
    match: MatchResponse
    readiness: ReadinessResponse
    gap: GapResponse