from pydantic import BaseModel


class GapRequest(BaseModel):
    skills: list[str]
    desired_role: str


class GapSkill(BaseModel):
    skill: str
    coverage_pct: float
    readiness_gain: float
    learn_with: list[str]


class GapResponse(BaseModel):
    recommendations: list[GapSkill]


class MatchRequest(BaseModel):
    skills: list[str]
    desired_role: str | None = None


class MatchRole(BaseModel):
    role_family: str
    probability: float


class MatchResponse(BaseModel):
    top_roles: list[MatchRole]
    unrecognized_skills: list[str]


class ReadinessRequest(BaseModel):
    skills: list[str]
    desired_role: str


class ReadinessResponse(BaseModel):
    desired_role: str
    probability: float
    readiness_band: str
    coverage_score: float