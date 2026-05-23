from pydantic import BaseModel
from typing import Dict, List, Optional


class ClassifiedItem(BaseModel):
    display_name: str
    category: str
    quantity: float
    unit: str


class ClassifyItemRequest(BaseModel):
    item_name: str
    household_size: Optional[int] = 2


class OnboardingRequest(BaseModel):
    household_items: List[str]
    goals: List[str]
    classified_items: Optional[Dict[str, ClassifiedItem]] = None
