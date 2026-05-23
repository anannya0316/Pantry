from db.collections import (
    profiles_collection,
    users_collection
)


def get_profile(user_id: str):
    return profiles_collection.find_one({
        "user_id": user_id
    })


def update_profile(
    user_id: str,
    updates: dict
):
    return profiles_collection.update_one(
        {"user_id": user_id},
        {"$set": updates}
    )


def get_auth_user(user_id: str):
    return users_collection.find_one({
        "_id": user_id
    })