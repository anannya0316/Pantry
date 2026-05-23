from pydantic import BaseModel

from typing import Optional


class LogRecipeRequest(BaseModel):
    meal_name: str

    meal_type: Optional[str] = None