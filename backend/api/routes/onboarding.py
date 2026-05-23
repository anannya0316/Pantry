from fastapi import APIRouter, BackgroundTasks, Header

from models.onboarding_models import ClassifyItemRequest, OnboardingRequest
from services.classification_service import classify_item
from services.onboarding_service import complete_onboarding


router = APIRouter()


@router.post("/classify-item")
def classify_item_route(data: ClassifyItemRequest):
    return classify_item(data.item_name, data.household_size)


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