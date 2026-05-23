from bson import ObjectId

from db.collections import (
    nutrition_logs_collection,
    profiles_collection
)


def insert_nutrition_log(log_data: dict):
    return nutrition_logs_collection.insert_one(
        log_data
    )


def get_nutrition_logs(user_id: str):
    return list(
        nutrition_logs_collection.find({
            "user_id": user_id
        })
    )


def get_profile(user_id: str):
    return profiles_collection.find_one(
        {"user_id": user_id}
    )


def get_nutrition_log_by_meal(user_id: str, meal_name: str):
    import re
    return list(
        nutrition_logs_collection.find({
            "user_id": user_id,
            "meal": {"$regex": re.escape(meal_name), "$options": "i"},
        })
    )


def update_nutrition_log(log_id: str, updates: dict):
    return nutrition_logs_collection.update_one(
        {"_id": ObjectId(log_id)},
        {"$set": updates},
    )