from pydantic import BaseModel

from typing import (
    List,
    Optional
)


class InventoryItem(BaseModel):
    display_name: str

    quantity: float

    unit: str

    category: Optional[str] = None

    purchase_date: Optional[str] = None

    status: Optional[str] = "fresh"


class AddInventoryRequest(BaseModel):
    items: List[InventoryItem]


class ClassifyRequest(BaseModel):
    display_name: str


class UpdateInventoryItem(BaseModel):
    index: int

    display_name: str

    quantity: float

    unit: str

    category: Optional[str] = None

    purchase_date: Optional[str] = None


class RecipeIngredient(BaseModel):
    name: str

    quantity: str

    unit: str


class UseRecipeRequest(BaseModel):
    ingredients: List[RecipeIngredient]

    have: List[str]

    need_to_buy: List[str]