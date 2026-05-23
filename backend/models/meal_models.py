from pydantic import BaseModel


class AddMealRequest(BaseModel):
    day: str

    meal_type: str

    meal_name: str


class DeleteMealRequest(BaseModel):
    day: str

    meal_type: str