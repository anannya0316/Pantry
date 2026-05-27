from datetime import (
    date,
    datetime,
    timedelta,
)

from fastapi import HTTPException

from constants.profile_constants import (
    TARGET_CATEGORIES
)

from dao.profile_dao import (
    get_profile
)

from dao.inventory_dao import (
    get_inventory,
    get_shelf_life
)

from dao.meal_dao import get_meal_plan

from utils.nutrition_utils import get_all_consumed_meals, get_active_meals
from utils.matching_utils import fuzzy_match

from dao.nutrition_dao import get_nutrition_logs

from utils.datetime_utils import parse_log_date


def get_profile_insights(
    user_id: str
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    profile = get_profile(user_id)

    inventory_doc = get_inventory(
        user_id
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    inventory = (
        inventory_doc.get("items", [])
        if inventory_doc else []
    )

    expiring = []

    for item in inventory:
        purchased = item.get(
            "purchased_date"
        )

        item_name = (
            item.get("display_name")
            or item.get("item_name")
        )

        if not purchased or not item_name:
            continue

        shelf_doc = get_shelf_life(
            item_name.strip().lower()
        )

        if not shelf_doc:
            continue

        try:
            expiry = (
                datetime.strptime(
                    purchased,
                    "%Y-%m-%d"
                ).date()
                + timedelta(
                    days=shelf_doc[
                        "shelf_life_days"
                    ]
                )
            )

            days_left = (
                expiry - date.today()
            ).days

            if days_left <= 2:
                expiring.append(
                    item_name
                )

        except Exception:
            continue

    waste_count = len(expiring)

    if waste_count <= 5:
        waste_risk = "Low"

    elif waste_count <= 7:
        waste_risk = "Medium"

    else:
        waste_risk = "High"

    waste_sub = (
        "No items expiring soon"
        if waste_count == 0
        else (
            f"{waste_count} item"
            f"{'s' if waste_count != 1 else ''}"
            f" expiring soon"
        )
    )

    meal_doc = get_meal_plan(user_id)
    active_meals = get_active_meals(meal_doc) if meal_doc else []
    all_ingredient_names = [
        ing["name"]
        for meal in active_meals
        for ing in meal.get("ingredients", [])
        if ing.get("name")
    ]

    if all_ingredient_names:
        in_stock = sum(
            1
            for name in all_ingredient_names
            if any(
                (
                    fuzzy_match(name, item.get("display_name", ""))
                    or any(
                        fuzzy_match(name, alias)
                        for alias in item.get("aliases", [])
                    )
                )
                and float(item.get("quantity", 0)) > 0
                for item in inventory
            )
        )
        grocery_efficiency = round(in_stock / len(all_ingredient_names) * 100)
    else:
        grocery_efficiency = 0

    if grocery_efficiency >= 80:
        grocery_sub = "Well stocked"

    elif grocery_efficiency >= 60:
        grocery_sub = "Good planning"

    else:
        grocery_sub = "Stock up needed"

    present_categories = {
        item.get("category")
        for item in inventory
        if (
            item.get("category")
            in TARGET_CATEGORIES
            and float(
                item.get(
                    "quantity",
                    0
                )
            ) > 0
        )
    }

    diet_balance_pct = round(
        len(present_categories)
        / len(TARGET_CATEGORIES)
        * 100
    )

    if diet_balance_pct >= 80:

        diet_label = "Excellent"

        diet_sub = "Well balanced"

    elif diet_balance_pct >= 60:

        diet_label = "Great"

        diet_sub = "Mostly balanced"

    elif diet_balance_pct >= 40:

        diet_label = "Good"

        diet_sub = "Getting there"

    else:

        diet_label = "Fair"

        diet_sub = "Needs more variety"

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    logs = get_nutrition_logs(user_id)
    log_scores = [
        log["health_score"]
        for log in logs
        if isinstance(log.get("health_score"), (int, float))
        and (d := parse_log_date(log)) is not None
        and monday <= d <= today
    ]

    meal_scores = [
        entry["health_score"]
        for entry in (get_all_consumed_meals(meal_doc) if meal_doc else [])
        if isinstance(entry.get("health_score"), (int, float))
    ]

    all_scores = log_scores + meal_scores
    health_alignment = (
        round(sum(all_scores) / len(all_scores))
        if all_scores else 0
    )

    if health_alignment >= 85:
        alignment_sub = (
            "On track with your goals"
        )

    elif health_alignment >= 70:
        alignment_sub = (
            "Making good progress"
        )

    else:
        alignment_sub = (
            "Needs attention"
        )

    return {
        "health_alignment":
            health_alignment,

        "health_alignment_sub":
            alignment_sub,

        "diet_balance":
            diet_label,

        "diet_balance_sub":
            diet_sub,

        "grocery_efficiency":
            grocery_efficiency,

        "grocery_efficiency_sub":
            grocery_sub,

        "food_waste_risk":
            waste_risk,

        "food_waste_count":
            waste_count,

        "food_waste_sub":
            waste_sub,
    }