from fastapi import HTTPException
from pydantic import BaseModel, Field

from services.nutrition_service import fetch_nutrition


# ── Pydantic schema ───────────────────────────────────────────────────────────

class LogRecipeInput(BaseModel):
    meal_name: str = Field(description="The name of the meal or recipe, e.g. 'grilled chicken salad'.")
    meal_type: str = Field(description="When the meal was eaten: 'breakfast', 'lunch', 'dinner', or 'snack'.")


class GetNutritionLogByMealInput(BaseModel):
    meal_name: str = Field(description="The meal name to search for, e.g. 'pasta'. Case-insensitive partial match.")
from services.health_score_service import calculate_meal_health_score
from services.nutrition_target_service import get_daily_targets
from utils.datetime_utils import now_utc
from dao.nutrition_dao import insert_nutrition_log, get_profile, get_nutrition_logs, get_nutrition_log_by_meal


def log_recipe(user_id: str, meal_name: str, meal_type: str):
    """Log nutrition and health score for a meal the user explicitly says they just ate."""
    try:
        if not user_id:
            return {"success": False, "error": "user_id is required"}

        if not meal_name or not meal_name.strip():
            return {"success": False, "error": "meal_name is required"}

        if not meal_type or not meal_type.strip():
            return {"success": False, "error": "meal_type is required"}

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

        return {
            "success": True,
            "message": "Nutrition log created successfully",
            "meal_name": meal_name,
            "meal_type": meal_type,
            "health_score": health_score,
        }

    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def get_all_nutrition_logs(user_id: str):
    """Return all nutrition log entries for the user."""
    try:
        logs = get_nutrition_logs(user_id)
        for log in logs:
            log.pop("_id", None)
        return {"success": True, "logs": logs}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def get_nutrition_log_by_meal_name(user_id: str, meal_name: str):
    """Return nutrition log entries matching a meal name (case-insensitive partial match)."""
    try:
        if not meal_name or not meal_name.strip():
            return {"success": False, "error": "meal_name is required"}
        logs = get_nutrition_log_by_meal(user_id, meal_name.strip())
        for log in logs:
            log.pop("_id", None)
        return {"success": True, "logs": logs}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# ── Backward-compat alias ─────────────────────────────────────────────────────
log_recipe_background = log_recipe
