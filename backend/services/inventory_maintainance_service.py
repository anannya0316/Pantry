from datetime import date

from db.collections import (
    inventory_collection,
    shelf_life_collection
)


def expire_stale_inventory(user_id: str):
    inventory_doc = inventory_collection.find_one(
        {"user_id": user_id}
    )

    if not inventory_doc or not inventory_doc.get("items"):
        return

    items = inventory_doc["items"]

    today = date.today()

    keys = [
        item["display_name"].strip().lower()
        for item in items
    ]

    shelf_map = {
        doc["item_key"]: doc["shelf_life_days"]
        for doc in shelf_life_collection.find(
            {"item_key": {"$in": keys}}
        )
    }

    updates = {}

    for idx, item in enumerate(items):
        purchase_date = item.get("purchase_date")

        if not purchase_date:
            continue

        shelf_days = shelf_map.get(
            item["display_name"].strip().lower()
        )

        if shelf_days is None:
            continue

        try:
            days_held = (
                today - date.fromisoformat(purchase_date)
            ).days

        except ValueError:
            continue

        if (
            days_held > shelf_days
            and float(item.get("quantity", 0)) > 0
        ):
            updates[f"items.{idx}.quantity"] = 0

    if updates:
        inventory_collection.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )