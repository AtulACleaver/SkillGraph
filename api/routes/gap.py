from fastapi import APIRouter

from api.schemas import GapRequest, GapResponse, GapSkill
from mining.gap import rank_gap

router = APIRouter()


@router.post(
    "/gap",
    response_model=GapResponse,
    tags=["Mining"],
    summary="Recommend Missing Skills",
    description="Returns the top 5 ranked skills a candidate should learn next to bridge the gap to their desired role.",
)
def post_gap(request: GapRequest):
    """
    POST /gap endpoint: returns top 5 ranked skills to learn next for the desired role.
    """
    recs = rank_gap(
        vector=request.skills,
        desired_role=request.desired_role,
        top_n=5,
    )
    formatted = [
        GapSkill(
            skill=r["skill"],
            coverage_pct=r["coverage_pct"],
            readiness_gain=r["readiness_gain"],
            learn_with=r["learn_with"],
        )
        for r in recs
    ]
    return GapResponse(recommendations=formatted)
