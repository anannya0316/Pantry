from db.collections import meal_plans_collection


def get_meal_plan(user_id: str):
    return meal_plans_collection.find_one({
        "user_id": user_id
    })


def update_meal_plan(
    user_id: str,
    meals: dict,
    updated_at,
    created_at=None
):
    update_data = {
        "$set": {
            "meals": meals,
            "updated_at": updated_at
        }
    }

    if created_at:
        update_data["$setOnInsert"] = {
            "created_at": created_at
        }

    return meal_plans_collection.update_one(
        {"user_id": user_id},
        update_data,
        upsert=True
    )

def get_user_meals(user_id: str):
    return list(
        meal_plans_collection.find({
            "user_id": user_id
        })
    )