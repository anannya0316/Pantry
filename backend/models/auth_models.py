from pydantic import BaseModel, EmailStr, Field

from models.enums import DietPreference, Weekday


class CreateAccountRequest(BaseModel):
    email: EmailStr

    password: str = Field(min_length=6)

    name: str

    phone: str

    household_size: int = Field(gt=0)

    diet: DietPreference

    cooking_frequency: str

    grocery_shopping_day: Weekday


class LoginRequest(BaseModel):
    email: EmailStr

    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class GoogleAuthRequest(BaseModel):
    credential: str

    mode: str

    household_size: int | None = None

    diet: str | None = None

    cooking_frequency: str | None = None

    grocery_shopping_day: Weekday | None = None