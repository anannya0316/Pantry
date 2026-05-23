from db.collections import shelf_life_collection


def enrich_with_shelf_life(
    inventory: list
) -> list:

    keys = []

    for item in inventory:
        name = item.get("display_name")

        keys.append(
            name.strip().lower()
        )

    docs = list(
        shelf_life_collection.find({
            "item_key": {
                "$in": keys
            }
        })
    )

    shelf_map = {
        doc["item_key"]: doc["shelf_life_days"]
        for doc in docs
    }

    enriched_items = []

    for item in inventory:
        name = item.get("display_name")

        enriched_items.append({
            **item,
            "shelf_life_days": shelf_map.get(
                name.strip().lower(),
                7
            )
        })

    return enriched_items