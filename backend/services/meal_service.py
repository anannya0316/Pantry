from datetime import date

from fastapi import HTTPException

from constants.meal_constants import (
    DAY_NAMES
)

from dao.meal_dao import (
    get_meal_plan,
    update_meal_plan
)

from db.collections import (
    inventory_collection,
    profiles_collection
)

from jobs.auto_consume import (
    auto_consume_past_meals
)

from jobs.weekly_restock import (
    get_monday,
    run_weekly_restock
)

from utils.unit_utils import (
    normalize_unit
)

from api.routes.shelf_life import (
    get_shelf_life
)

from services.ingredient_service import (
    fetch_ingredients
)

from services.nutrition_service import (
    store_nutrition_nested
)

from utils.matching_utils import (
    fuzzy_match
)

from utils.datetime_utils import (
    now_ist,
    now_utc
)

from services.classification_service import classify_item

def classify_and_update(
    user_id,
    display_name,
    household_size
):
    classified = classify_item(
        display_name,
        household_size
    )

    inventory_doc = inventory_collection.find_one(
        {"user_id": user_id}
    )

    if not inventory_doc:
        return

    inventory = inventory_doc.get(
        "items",
        []
    )

    for idx, inv_item in enumerate(inventory):

        if fuzzy_match(
            display_name,
            inv_item.get("display_name", "")
        ):

            inventory_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"items.{idx}.category":
                        classified["category"]
                    }
                }
            )

            break


def get_meal_plan_service(
    background_tasks,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    today = now_ist().date()

    cur_monday = get_monday(today)

    auto_consume_past_meals(
        user_id,
        today
    )

    restocked = run_weekly_restock(
        user_id,
        cur_monday
    )

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:
        return {
            "meals": {},
            "restocked": restocked
        }

    return {
        "meals": meal_doc.get("meals", {}),
        "restocked": restocked
    }


def add_meal(
    request,
    background_tasks,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    now = now_utc()

    user = profiles_collection.find_one(
        {"user_id": user_id},
        {
            "household_size": 1,
            "diet": 1,
            "allergies": 1,
            "spice_preference": 1,
            "liked_ingredients": 1,
            "disliked_ingredients": 1,
            "favorite_cuisines": 1,
            "special_preferences": 1,
        }
    )

    household_size = (
        user.get("household_size", 2)
        if user else 2
    )

    def _get(key):
        return user.get(key) or None if user else None

    preferences = {
        k: v for k, v in {
            "diet":                 _get("diet"),
            "allergies":            _get("allergies"),
            "spice_preference":     _get("spice_preference"),
            "liked_ingredients":    _get("liked_ingredients"),
            "disliked_ingredients": _get("disliked_ingredients"),
            "favorite_cuisines":    _get("favorite_cuisines"),
            "special_preferences":  _get("special_preferences"),
        }.items() if v is not None
    }

    ingredients = fetch_ingredients(
        request.meal_name,
        household_size,
        preferences,
    )

    inventory_doc = inventory_collection.find_one({
        "user_id": user_id
    })

    inventory = (
        inventory_doc.get("items", [])
        if inventory_doc else []
    )

    new_items = []

    qty_updates = {}

    for ing in ingredients:

        found_idx = next(
            (
                i for i, inv in enumerate(inventory)
                if fuzzy_match(
                    ing["name"],
                    inv.get("display_name", "")
                )
            ),
            None
        )

        if found_idx is None:

            new_item = {
                "display_name": ing["name"],
                "quantity": ing["quantity"],
                "unit": normalize_unit(
                    ing["unit"]
                ),
                "category": "Other",
                "purchase_date": date.today().isoformat(),
                "status": "fresh"
            }

            new_items.append(new_item)

            inventory.append(new_item)

        elif (
            float(
                inventory[found_idx].get(
                    "quantity",
                    0
                )
            ) <= 0
        ):

            qty_updates[
                f"items.{found_idx}.quantity"
            ] = ing["quantity"]

            inventory[found_idx]["quantity"] = (
                ing["quantity"]
            )

    if qty_updates:
        inventory_collection.update_one(
            {"user_id": user_id},
            {"$set": qty_updates}
        )

    if new_items:

        inventory_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "items": {
                        "$each": new_items
                    }
                }
            },
            upsert=True
        )

        for item in new_items:

            background_tasks.add_task(
                classify_and_update,
                user_id,
                item["display_name"],
                household_size
            )

            background_tasks.add_task(
                get_shelf_life,
                item["display_name"]
            )

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:

        meal_doc = {
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "meals": {
                day: {
                    "breakfast": [],
                    "lunch": [],
                    "dinner": []
                }
                for day in DAY_NAMES
            }
        }

    meals = meal_doc["meals"]

    slot_meals = meals[
        request.day
    ][
        request.meal_type
    ]

    for meal in slot_meals:

        if meal.get("valid") is True:

            meal["valid"] = False

            meal["updated_at"] = now

    meal = {
        "meal_name": request.meal_name,
        "ingredients": ingredients,
        "nutrition": {},
        "consumed": False,
        "skipped": False,
        "valid": True,
        "created_at": now,
        "updated_at": now,
    }

    slot_meals.append(meal)

    meal_doc["updated_at"] = now

    update_meal_plan(
        user_id,
        meals,
        now,
        created_at=now
    )

    background_tasks.add_task(
        store_nutrition_nested,
        user_id,
        request.day,
        request.meal_type,
        request.meal_name
    )

    return {
        "message": "Meal added",
        "ingredients": ingredients
    }


def delete_meal(
    request,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:
        raise HTTPException(
            status_code=404,
            detail="Meal plan not found"
        )

    meals = meal_doc.get("meals", {})

    slot_meals = meals.get(
        request.day,
        {}
    ).get(
        request.meal_type,
        []
    )

    found = False

    for meal in reversed(slot_meals):

        if meal.get("valid") is True:

            meal["valid"] = False
            meal["skipped"] = True
            meal["updated_at"] = now_utc()

            found = True

            break

    if not found:
        raise HTTPException(
            status_code=404,
            detail="Meal not found"
        )

    update_meal_plan(
        user_id,
        meals,
        now_utc()
    )

    return {
        "message": "Meal deleted"
    }