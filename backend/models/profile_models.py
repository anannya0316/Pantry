from pydantic import BaseModel

from typing import (
    List,
    Optional
)

from models.enums import (
    Weekday,
    DietPreference
)


class UpdateGoalsRequest(BaseModel):
    goals: List[str]


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None

    phone: Optional[str] = None

    household_size: Optional[int] = None

    diet: Optional[DietPreference] = None

    cooking_frequency: Optional[str] = None

    goals: Optional[List[str]] = None

    allergies: Optional[List[str]] = None

    spice_preference: Optional[str] = None

    liked_ingredients: Optional[List[str]] = None

    disliked_ingredients: Optional[List[str]] = None

    favorite_cuisines: Optional[List[str]] = None

    special_preferences: Optional[List[str]] = None

    grocery_shopping_day: Optional[
        Weekday
    ] = None