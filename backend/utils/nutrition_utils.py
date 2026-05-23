from constants.nutrition_constants import (
    MACRO_KEYS
)


def sum_nutrition(meals: list) -> dict:
    totals = {
        k: 0.0
        for k in MACRO_KEYS
    }

    for meal in meals:
        nutrition = meal.get(
            "nutrition"
        ) or {}

        for key in MACRO_KEYS:
            totals[key] += nutrition.get(
                key,
                0.0
            )

    return totals


def get_active_meals(
    meal_doc: dict
) -> list:

    active_meals = []

    meals = meal_doc.get(
        "meals",
        {}
    )

    for day_name, day_data in meals.items():

        for meal_type, slot_meals in day_data.items():

            for meal in reversed(slot_meals):

                if (
                    meal.get("valid") is True
                    and meal.get("skipped") is not True
                ):

                    enriched_meal = {
                        **meal,
                        "day": day_name,
                        "meal_type": meal_type,
                    }

                    active_meals.append(
                        enriched_meal
                    )

                    break

    return active_meals


def get_all_consumed_meals(meal_doc: dict) -> list:
    """Return every meal entry across all slots and versions where consumed=True."""
    consumed = []
    for day_name, day_data in meal_doc.get("meals", {}).items():
        for meal_type, slot_meals in day_data.items():
            for meal in slot_meals:
                if meal.get("consumed") is True:
                    consumed.append({
                        **meal,
                        "day": day_name,
                        "meal_type": meal_type,
                    })
    return consumed