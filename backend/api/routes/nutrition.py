from fastapi import (
    APIRouter,
    BackgroundTasks,
    Header,
    HTTPException
)

from models.nutrition_models import (
    LogRecipeRequest
)

from services.nutrition_logging_service import (
    log_recipe_background
)

from services.nutrition_insights_service import (
    get_nutrition_insights
)

from utils.datetime_utils import now_ist

router = APIRouter()


@router.post("/log-recipe")
def log_recipe(
    request: LogRecipeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None)
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    if request.meal_type:
        meal_type = request.meal_type

    else:
        hour = now_ist().hour

        meal_type = (
            "breakfast"
            if hour < 10
            else (
                "lunch"
                if hour < 15
                else "dinner"
            )
        )

    background_tasks.add_task(
        log_recipe_background,
        user_id,
        request.meal_name,
        meal_type
    )

    return {
        "message": "Meal logged"
    }


@router.get("/insights")
def nutrition_insights(
    period: str = "weekly",
    user_id: str = Header(None)
):
    return get_nutrition_insights(
        user_id,
        period=period
    )