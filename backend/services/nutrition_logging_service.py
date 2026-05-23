from services.nutrition_service import (
    fetch_nutrition)

from services.health_score_service import (
    calculate_meal_health_score
)

from services.nutrition_target_service import (
    get_daily_targets
)

from utils.datetime_utils import (
    now_utc
)

from dao.nutrition_dao import (
    insert_nutrition_log,
    get_profile,
)


def log_recipe_background(
    user_id: str,
    meal_name: str,
    meal_type: str
):
    nutrition = fetch_nutrition(meal_name)
    created_at = now_utc()

    user = get_profile(user_id)
    goals = user.get("goals", []) if user else []
    daily_targets = get_daily_targets(goals)

    health_score = calculate_meal_health_score(
        meal_name=meal_name,
        nutrition=nutrition,
        meal_type=meal_type,
        created_at=created_at,
        daily_targets=daily_targets,
    )

    insert_nutrition_log({
        "user_id": user_id,
        "meal": meal_name,
        "meal_type": meal_type,
        "nutrition": nutrition,
        "health_score": health_score,
        "created_at": created_at,
    })