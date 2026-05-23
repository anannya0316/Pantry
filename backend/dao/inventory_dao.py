from db.collections import (
    inventory_collection,
    profiles_collection,
    users_collection,
    shelf_life_collection
)


def get_user_inventory(user_id: str):
    return inventory_collection.find_one({
        "user_id": user_id
    })


def update_inventory(
    user_id: str,
    items: list
):
    return inventory_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": items}}
    )


def push_inventory_items(
    user_id: str,
    items: list
):
    return inventory_collection.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "items": {
                    "$each": items
                }
            }
        },
        upsert=True
    )


def update_inventory_item_by_index(
    user_id: str,
    index: int,
    item: dict
):
    return inventory_collection.update_one(
        {"user_id": user_id},
        {"$set": {f"items.{index}": item}}
    )


def update_inventory_fields(
    user_id: str,
    updates: dict
):
    return inventory_collection.update_one(
        {"user_id": user_id},
        {"$set": updates}
    )


def get_profile(user_id: str):
    return profiles_collection.find_one({
        "user_id": user_id
    })


def get_user(user_id: str):
    return users_collection.find_one({
        "_id": user_id
    })

def get_inventory(user_id: str):
    return inventory_collection.find_one({
        "user_id": user_id
    })


def get_shelf_life(item_key: str):
    return shelf_life_collection.find_one({
        "item_key": item_key
    })