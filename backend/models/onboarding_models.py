from pydantic import BaseModel
from typing import List


class OnboardingRequest(BaseModel):
    household_items: List[str]

    goals: List[str]