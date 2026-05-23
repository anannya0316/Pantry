from constants.profile_constants import (
    MEAT_WORDS
)


def is_vegetarian_profile(
    diet
):
    if isinstance(diet, str):
        diet = [diet]

    return any(
        "veg" in pref.lower()
        for pref in diet
    )


def is_meal_veg(
    meal: dict
):
    meal_name = meal.get(
        "meal_name",
        ""
    ).lower()

    ingredients = meal.get(
        "ingredients",
        []
    )

    return not any(
        meat_word in meal_name
        or any(
            meat_word in ingredient[
                "name"
            ].lower()
            for ingredient in ingredients
        )
        for meat_word in MEAT_WORDS
    )