from datetime import timedelta

from constants.meal_constants import (
    DAY_NAMES,
    MEAL_CUTOFF
)

from dao.meal_dao import (
    get_meal_plan,
    update_meal_plan
)

from db.collections import (
    inventory_collection,
    profiles_collection
)

from services.meal_inventory_service import (
    deduct_ingredients
)

from utils.datetime_utils import (
    now_utc,
    now_ist
)


def _get_cycle_start(today, grocery_shopping_day: str):
    """Returns the most recent occurrence of grocery_shopping_day on or before today."""
    try:
        shopping_dow = DAY_NAMES.index(grocery_shopping_day)
    except ValueError:
        shopping_dow = 0  # default Monday

    days_since = (today.weekday() - shopping_dow) % 7

    return today - timedelta(days=days_since)


def auto_consume_past_meals(
    user_id,
    today
):
    profile = profiles_collection.find_one(
        {"user_id": user_id},
        {"grocery_shopping_day": 1}
    )

    grocery_shopping_day = (
        profile.get("grocery_shopping_day")
        if profile else None
    ) or "Monday"

    today_dow = today.weekday()

    monday_of_week = today - timedelta(days=today_dow)

    cycle_start = _get_cycle_start(today, grocery_shopping_day)

    effective_start = max(cycle_start, monday_of_week)
    effective_start_dow = effective_start.weekday()

    past_day_names = DAY_NAMES[effective_start_dow:today_dow]

    current_hour = now_ist().hour

    past_types_today = [
        mt
        for mt, cutoff in MEAL_CUTOFF.items()
        if current_hour >= cutoff
    ]

    today_name = DAY_NAMES[today_dow]

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:
        return

    meals = meal_doc.get("meals", {})

    inventory_doc = inventory_collection.find_one({
        "user_id": user_id
    })

    inventory = (
        inventory_doc.get("items", [])
        if inventory_doc else []
    )

    all_updates = {}

    now = now_utc()

    for day in past_day_names:
        day_data = meals.get(day, {})

        for slot_meals in day_data.values():

            for meal in reversed(slot_meals):

                if (
                    meal.get("valid") is True
                    and meal.get("skipped") is not True
                    and meal.get("consumed") is not True
                ):

                    updates = deduct_ingredients(
                        inventory,
                        meal.get("ingredients", [])
                    )

                    all_updates.update(updates)

                    meal["consumed"] = True
                    meal["updated_at"] = now

                    break

    today_data = meals.get(today_name, {})

    for meal_type in past_types_today:

        slot_meals = today_data.get(meal_type, [])

        for meal in reversed(slot_meals):

            if (
                meal.get("valid") is True
                and meal.get("skipped") is not True
                and meal.get("consumed") is not True
            ):

                updates = deduct_ingredients(
                    inventory,
                    meal.get("ingredients", [])
                )

                all_updates.update(updates)

                meal["consumed"] = True
                meal["updated_at"] = now

                break

    if all_updates:
        inventory_collection.update_one(
            {"user_id": user_id},
            {"$set": all_updates}
        )

    update_meal_plan(
        user_id,
        meals,
        now
    )
