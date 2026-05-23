from datetime import (
    date,
    datetime,
    timezone
)

from fastapi import HTTPException

from db.collections import (
    profiles_collection,
    inventory_collection
)

from services.classification_service import classify_item

from services.shelf_life_service import get_shelf_life


def complete_onboarding(
    data,
    background_tasks,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    profile = profiles_collection.find_one(
        {"user_id": user_id},
        {"household_size": 1}
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    household_size = profile.get(
        "household_size",
        1
    )

    today = date.today().isoformat()

    now = datetime.now(timezone.utc)

    inventory_items = []

    pre = data.classified_items or {}

    for item_name in data.household_items:
        if item_name in pre:
            c = pre[item_name]
            classified = {
                "display_name": c.display_name,
                "category": c.category,
                "quantity": c.quantity,
                "unit": c.unit,
            }
        else:
            classified = classify_item(item_name, household_size)

        input_name = item_name.strip().lower()

        resolved_name = classified.get(
            "display_name",
            input_name
        )

        inventory_items.append({
            "display_name": resolved_name.title(),
            "aliases": (
                [input_name]
                if input_name != resolved_name
                else []
            ),
            "quantity": classified["quantity"],
            "unit": classified["unit"],
            "category": classified["category"],
            "purchase_date": today,
            "status": "fresh"
        })

    profiles_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "goals": data.goals,
                "updated_at": now
            }
        }
    )

    inventory_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "items": inventory_items,
                "updated_at": now
            }
        }
    )

    for item_name in data.household_items:
        background_tasks.add_task(
            get_shelf_life,
            item_name
        )

    return {
        "message": "Onboarding completed",
        "user_id": user_id
    }