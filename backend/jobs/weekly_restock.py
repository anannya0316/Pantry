from datetime import timedelta

from constants.meal_constants import (
    DAY_NAMES
)

from dao.meal_dao import (
    get_meal_plan,
    update_meal_plan
)

from db.collections import inventory_collection

from services.meal_inventory_service import (
    fuzzy_inventory_match
)

from utils.unit_utils import (
    normalize_unit
)

from utils.datetime_utils import (
    now_utc
)


def get_monday(d):
    return d - timedelta(days=d.weekday())


def run_weekly_restock(
    user_id,
    current_monday
):
    inventory_doc = inventory_collection.find_one(
        {
            "user_id": user_id
        },
        {
            "items": 1,
            "last_restock_week": 1
        }
    )

    if not inventory_doc:
        return False

    current_monday_str = current_monday.isoformat()

    if (
        inventory_doc.get("last_restock_week")
        == current_monday_str
    ):
        return False

    inventory = inventory_doc.get("items", [])

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:
        return False

    meals = meal_doc.get("meals", {})

    add_back = {}

    for day_data in meals.values():

        for slot_meals in day_data.values():

            active_meal = None

            for meal in reversed(slot_meals):

                if (
                    meal.get("valid") is True
                    and meal.get("skipped") is not True
                ):
                    active_meal = meal
                    break

            if not active_meal:
                continue

            for ing in active_meal.get(
                "ingredients",
                []
            ):

                for idx, inv_item in enumerate(inventory):

                    if fuzzy_inventory_match(
                        ing["name"],
                        inv_item["display_name"]
                    ):

                        norm_unit = normalize_unit(
                            ing.get("unit", "unit")
                        )

                        qty = (
                            float(ing.get("quantity", 1))
                            if norm_unit == inv_item["unit"]
                            else 1
                        )

                        add_back[idx] = (
                            add_back.get(idx, 0)
                            + qty
                        )

                        break

    sunday_date = (
        current_monday - timedelta(days=1)
    ).isoformat()

    updates = {
        "last_restock_week": current_monday_str
    }

    for idx, qty in add_back.items():

        current_qty = float(
            inventory[idx].get("quantity", 0)
        )

        updates[f"items.{idx}.quantity"] = (
            current_qty + qty
        )

        updates[f"items.{idx}.purchase_date"] = (
            sunday_date
        )

    inventory_collection.update_one(
        {"user_id": user_id},
        {"$set": updates}
    )

    now = now_utc()

    for day_data in meals.values():

        for slot_meals in day_data.values():

            for meal in reversed(slot_meals):

                if meal.get("valid") is True:

                    meal["consumed"] = False
                    meal["skipped"] = False
                    meal["updated_at"] = now

                    break

    update_meal_plan(
        user_id,
        meals,
        now
    )

    return bool(add_back)