from pydantic import BaseModel, ConfigDict


class GapRequest(BaseModel):
    skills: list[str]
    desired_role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skills": ["python", "sql", "pandas"],
                "desired_role": "Data Science / ML"
            }
        }
    )


class GapSkill(BaseModel):
    skill: str
    coverage_pct: float
    readiness_gain: float
    learn_with: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skill": "Scikit-Learn",
                "coverage_pct": 0.85,
                "readiness_gain": 0.125,
                "learn_with": ["Numpy", "Tensorflow"]
            }
        }
    )


class GapResponse(BaseModel):
    recommendations: list[GapSkill]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendations": [
                    {
                        "skill": "Scikit-Learn",
                        "coverage_pct": 0.85,
                        "readiness_gain": 0.125,
                        "learn_with": ["Numpy", "Tensorflow"]
                    }
                ]
            }
        }
    )


class MatchRequest(BaseModel):
    skills: list[str]
    desired_role: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skills": ["react", "typescript", "css"],
                "desired_role": "Frontend"
            }
        }
    )


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