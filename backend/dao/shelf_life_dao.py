from db.collections import shelf_life_collection


def get_shelf_life_doc(
    item_key: str
):
    return shelf_life_collection.find_one({
        "item_key": item_key
    })


def upsert_shelf_life(
    item_key: str,
    shelf_life_days: int,
    updated_at: str
):
    return shelf_life_collection.update_one(
        {
            "item_key": item_key
        },
        {
            "$set": {
                "item_key": item_key,
                "shelf_life_days": shelf_life_days,
                "updated_at": updated_at
            }
        },
        upsert=True
    )