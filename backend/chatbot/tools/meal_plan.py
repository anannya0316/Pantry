import threading
from typing import Optional, List

from fastapi import BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from models.meal_models import AddMealRequest, DeleteMealRequest
from services.meal_service import (
    get_meal_plan_service,
    add_meal as add_meal_service,
    delete_meal as delete_meal_service,
)
from services.nutrition_service import store_nutrition_nested


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class MealPlanItem(BaseModel):
    meal_name: str = Field(..., description="The name of the meal in the week.")
    meal_day: str = Field(..., description="The day of the week for the meal.")
    meal_type: str = Field(..., description="The type of the meal, e.g., breakfast, lunch, dinner.")
    ingredients: List[str] = Field(..., description="List of ingredients needed for the meal.")
    nutrition_info: Optional[List[str]] = Field(default=None, description="Nutrition information for the meal.")
    status: str = Field(..., description="The status of the meal plan item, e.g., planned, completed, skipped.")
    created_at: str = Field(..., description="The date when the meal plan item was created.")


_MEAL_PLAN_TYPES = {"breakfast", "lunch", "dinner"}

class AddMealPlanItemInput(BaseModel):
    meal_name: str = Field(description="Name of the meal, e.g., 'Chicken Curry'")
    meal_day: str = Field(description="The day of the week for the meal, e.g., 'Monday'")
    meal_type: str = Field(description="Must be 'breakfast', 'lunch', or 'dinner'. Snacks and other types cannot be added to the meal plan.")
    created_at: Optional[str] = Field(default=None, description="Use today's date if not stated by the user.")
    status: Optional[str] = Field(default="planned", description="Status of the meal plan item, e.g., 'planned', 'completed', 'skipped'")


class UpdateMealPlanItemInput(BaseModel):
    meal_name: str = Field(description="Name of the meal to update.")
    meal_day: Optional[str] = Field(default=None, description="New day of the week, if user gave it.")
    meal_type: Optional[str] = Field(default=None, description="New type — must be 'breakfast', 'lunch', or 'dinner'.")
    status: Optional[str] = Field(default=None, description="New status, if user gave it.")


class GetMealPlanItemInput(BaseModel):
    meal_name: Optional[str] = Field(default=None, description="Name of the meal to retrieve; omit to fetch the full plan.")
    meal_day: Optional[str] = Field(default=None, description="Day of the week for the meal, if user gave it.")
    meal_type: Optional[str] = Field(default=None, description="Type of the meal, if user gave it.")
    status: Optional[str] = Field(default=None, description="Status of the meal plan item, e.g., 'planned', 'completed', 'skipped'.")


def get_meal_plan_item(
    user_id: str,
    meal_name: str = None,
    meal_day: str = None,
    meal_type: str = None,
    status: str = None,
):
    """Fetch all meals in the meal plan, optionally filtered by day, type, or status."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    try:
        result = get_meal_plan_service(BackgroundTasks(), user_id)
        return {"success": True, "data": result}

    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def update_meal_plan_item(
    user_id: str,
    meal_name: str,
    meal_day: str = None,
    meal_type: str = None,
    status: str = None,
):
    """Update an existing meal plan entry — reschedule to a new day or meal type."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    if not meal_day or not meal_type:
        missing = []
        if not meal_day:
            missing.append("meal_day")
        if not meal_type:
            missing.append("meal_type")
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing)}.",
            "missing_fields": missing,
        }

    if meal_type.lower() not in _MEAL_PLAN_TYPES:
        return {
            "success": False,
            "error": f"'{meal_type}' cannot be added to the meal plan. Only breakfast, lunch, and dinner are allowed. Log snacks or other meals via the nutrition log instead.",
        }

    try:
        request = AddMealRequest(day=meal_day, meal_type=meal_type, meal_name=meal_name)
        result = add_meal_service(request, BackgroundTasks(), user_id)
        threading.Thread(
            target=store_nutrition_nested,
            args=(user_id, meal_day, meal_type, meal_name),
            daemon=True,
        ).start()
        return {
            "success": True,
            "message": result.get("message", "Meal plan updated successfully"),
            "ingredients": result.get("ingredients", []),
        }

    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def add_meal(
    user_id: str,
    meal_name: str,
    meal_day: str,
    meal_type: str,
    created_at: str = None,
    status: str = None,
):
    """Add a new meal to the weekly plan."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    if meal_type.lower() not in _MEAL_PLAN_TYPES:
        return {
            "success": False,
            "error": f"'{meal_type}' cannot be added to the meal plan. Only breakfast, lunch, and dinner are allowed. Log snacks or other meals via the nutrition log instead.",
        }

    try:
        request = AddMealRequest(day=meal_day, meal_type=meal_type, meal_name=meal_name)
        result = add_meal_service(request, BackgroundTasks(), user_id)
        threading.Thread(
            target=store_nutrition_nested,
            args=(user_id, meal_day, meal_type, meal_name),
            daemon=True,
        ).start()
        return {
            "success": True,
            "message": result.get("message", "Meal added successfully"),
            "ingredients": result.get("ingredients", []),
        }

    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def delete_meal_tool(user_id: str, day: str, meal_type: str):
    """Delete a meal from the plan (kept for internal use by nutrition_router)."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    try:
        request = DeleteMealRequest(day=day, meal_type=meal_type)
        result = delete_meal_service(request, user_id)
        return {
            "success": True,
            "message": result.get("message", "Meal deleted successfully"),
        }

    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# ── Backward-compat aliases (used by dispatch.py / nutrition_router / evals) ─
get_meal_plan = get_meal_plan_item
add_meal_tool = add_meal
