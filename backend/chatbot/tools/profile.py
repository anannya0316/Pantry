from typing import Optional, List

from pydantic import BaseModel, Field

from dao.profile_dao import (
    get_profile as _get_profile_dao,
    update_profile as _update_profile_dao,
    get_auth_user,
)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class Profile(BaseModel):
    name: str = Field(..., description="The name of the user.")
    phone: str = Field(..., description="The phone number of the user.")
    household_size: int = Field(..., description="The number of people in the user's household.")
    cooking_frequency: str = Field(..., description="How often the user cooks meals at home.")
    grocery_shopping_day: str = Field(..., description="The user's weekly shopping day where inventory will be restocked.")
    diet: str = Field(..., description="The user's diet preference — e.g., 'veg' or 'non_veg'.")
    goals: List[str] = Field(..., description="The user's health or dietary goals.")
    allergies: List[str] = Field(..., description="Any allergies or intolerances the user has.")
    spice_preference: str = Field(..., description="The user's spice tolerance — e.g., 'Mild', 'Medium', 'Hot'.")
    disliked_ingredients: List[str] = Field(..., description="Ingredients the user dislikes.")
    favorite_cuisines: List[str] = Field(..., description="The user's favourite cuisines.")
    liked_ingredients: List[str] = Field(..., description="Ingredients the user enjoys.")
    special_preferences: List[str] = Field(..., description="Any special dietary preferences — e.g., 'gluten-free', 'low sugar'.")


class UpdateProfileInput(BaseModel):
    household_size: Optional[int] = Field(default=None, description="New household size.")
    cooking_frequency: Optional[str] = Field(default=None, description="New cooking frequency.")
    grocery_shopping_day: Optional[str] = Field(default=None, description="New grocery shopping day.")
    diet: Optional[str] = Field(default=None, description="New diet preference. Use 'veg' for vegetarian/vegan, 'non_veg' for non-vegetarian.")
    goals: Optional[List[str]] = Field(default=None, description="Updated list of health or dietary goals.")
    allergies: Optional[List[str]] = Field(default=None, description="Updated list of allergies or intolerances.")
    spice_preference: Optional[str] = Field(default=None, description="New spice preference — e.g., 'Mild', 'Medium', 'Hot'.")
    disliked_ingredients: Optional[List[str]] = Field(default=None, description="Updated list of disliked ingredients.")
    favorite_cuisines: Optional[List[str]] = Field(default=None, description="Updated list of favourite cuisines.")
    liked_ingredients: Optional[List[str]] = Field(default=None, description="Updated list of liked ingredients.")
    special_preferences: Optional[List[str]] = Field(default=None, description="Updated list of special dietary preferences.")


ALLOWED_DIET_TYPES = {"veg", "non_veg"}

_DIET_ALIASES = {
    "vegetarian": "veg",
    "vegan": "veg",
    "plant-based": "veg",
    "plant based": "veg",
    "non-vegetarian": "non_veg",
    "non vegetarian": "non_veg",
    "nonvegetarian": "non_veg",
    "omnivore": "non_veg",
    "meat eater": "non_veg",
}

ALLOWED_WEEKDAYS = {
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
}

VALID_GOALS = {
    "Eat healthier",
    "Save money",
    "Cook faster",
    "Gain muscle",
    "Lose weight",
}


def get_profile(user_id: str):
    """Fetch the user's full profile."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    try:
        profile = _get_profile_dao(user_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        auth = get_auth_user(user_id)
        if auth:
            profile["email"] = auth.get("email")

        if "_id" in profile:
            profile["_id"] = str(profile["_id"])

        return {"success": True, "profile": profile}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def update_profile(
    user_id: str,
    household_size: int = None,
    cooking_frequency: str = None,
    grocery_shopping_day: str = None,
    diet: str = None,
    goals: list = None,
    allergies: list = None,
    spice_preference: str = None,
    disliked_ingredients: list = None,
    favorite_cuisines: list = None,
    liked_ingredients: list = None,
    special_preferences: list = None,
):
    """Update one or more fields of the user's profile. Name and phone cannot be changed."""
    if not user_id:
        return {"success": False, "error": "user_id is required"}

    try:
        updates = {k: v for k, v in {
            "household_size": household_size,
            "cooking_frequency": cooking_frequency,
            "grocery_shopping_day": grocery_shopping_day,
            "diet": diet,
            "goals": goals,
            "allergies": allergies,
            "spice_preference": spice_preference,
            "disliked_ingredients": disliked_ingredients,
            "favorite_cuisines": favorite_cuisines,
            "liked_ingredients": liked_ingredients,
            "special_preferences": special_preferences,
        }.items() if v is not None}

        if not updates:
            return {"success": False, "error": "No fields provided to update."}

        if "diet" in updates:
            updates["diet"] = _DIET_ALIASES.get(updates["diet"].lower().strip(), updates["diet"])
            if updates["diet"] not in ALLOWED_DIET_TYPES:
                return {"success": False, "error": f"Invalid diet. Allowed values: {sorted(ALLOWED_DIET_TYPES)}"}

        if "grocery_shopping_day" in updates and updates["grocery_shopping_day"] not in ALLOWED_WEEKDAYS:
            return {"success": False, "error": f"Invalid grocery_shopping_day. Allowed values: {sorted(ALLOWED_WEEKDAYS)}"}

        if "goals" in updates:
            if not isinstance(updates["goals"], list):
                return {"success": False, "error": "goals must be a list"}
            invalid = [g for g in updates["goals"] if g not in VALID_GOALS]
            if invalid:
                return {"success": False, "error": f"Invalid goals: {invalid}. Allowed values: {sorted(VALID_GOALS)}"}

        if "household_size" in updates:
            if not isinstance(updates["household_size"], int) or updates["household_size"] < 1:
                return {"success": False, "error": "household_size must be an integer >= 1"}

        for list_field in ("allergies", "liked_ingredients", "disliked_ingredients", "favorite_cuisines", "special_preferences"):
            if list_field in updates and not isinstance(updates[list_field], list):
                return {"success": False, "error": f"{list_field} must be a list"}

        result = _update_profile_dao(user_id, updates)

        if result.matched_count == 0:
            return {"success": False, "error": "Profile not found"}

        return {
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(updates.keys()),
            "updates": updates,
        }

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# ── Backward-compat aliases (used by dispatch.py / evals) ───────────────────
get_user_profile = get_profile
update_user_profile = update_profile
