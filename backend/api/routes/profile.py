from fastapi import (
    APIRouter,
    Header
)

from models.profile_models import (
    UpdateGoalsRequest,
    UpdateProfileRequest
)

from services.profile_service import (
    get_user_profile,
    update_user_goals,
    update_user_profile
)

from services.profile_insights_service import (
    get_profile_insights
)

router = APIRouter()


@router.get("/")
def get_profile_route(
    user_id: str = Header(None)
):
    return get_user_profile(
        user_id
    )


@router.put("/update-goals")
def update_goals_route(
    request: UpdateGoalsRequest,
    user_id: str = Header(None)
):
    return update_user_goals(
        request,
        user_id
    )


@router.put("/update")
def update_profile_route(
    request: UpdateProfileRequest,
    user_id: str = Header(None)
):
    return update_user_profile(
        request,
        user_id
    )


@router.get("/insights")
def insights_route(
    user_id: str = Header(None)
):
    return get_profile_insights(
        user_id
    )