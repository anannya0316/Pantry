from fastapi import APIRouter, BackgroundTasks, Header

from models.onboarding_models import OnboardingRequest
from services.onboarding_service import complete_onboarding


router = APIRouter()


@router.post("/complete-onboarding")
def complete_onboarding_route(
    data: OnboardingRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None)
):
    return complete_onboarding(
        data,
        background_tasks,
        user_id
    )