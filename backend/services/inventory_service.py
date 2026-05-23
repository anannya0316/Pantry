from fastapi import HTTPException

from dao.inventory_dao import (
    get_user_inventory,
    update_inventory,
    push_inventory_items,
    update_inventory_item_by_index,
    get_profile,
    get_user
)

from services.classification_service import classify_item

from utils.inventory_utils import (
    enrich_with_shelf_life
)

from api.routes.shelf_life import (
    get_shelf_life
)


def classify_inventory_item(
    request,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    user = get_user(user_id)

    household_size = 1

    if user:
        household_size = user.get(
            "household_size",
            1
        )

    try:
        return classify_item(
            request.display_name,
            household_size
        )

    except Exception as e:
        print(f"Classification Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Failed to classify item"
        )


def reclassify_inventory(user_id):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    household_size = user.get(
        "household_size",
        1
    )

    inventory_doc = get_user_inventory(user_id)

    if not inventory_doc:
        return {
            "message": "No items found to reclassify",
            "count": 0
        }

    inventory = inventory_doc.get("items", [])

    updated = []

    for item in inventory:
        name_to_classify = item.get(
            "display_name"
        )

        try:
            classified = classify_item(
                name_to_classify,
                household_size
            )

            updated_item = {
                **item,
                "category": classified.get(
                    "category",
                    item.get("category")
                ),
                "quantity": classified.get(
                    "quantity",
                    item.get("quantity")
                ),
                "unit": classified.get(
                    "unit",
                    item.get("unit")
                )
            }

            updated.append(updated_item)

        except Exception as e:
            print(
                f"Skipping reclassification "
                f"for {name_to_classify}: {e}"
            )

            updated.append(item)

    update_inventory(
        user_id,
        updated
    )

    return {
        "message": f"Reclassified {len(updated)} items"
    }


def update_inventory_item(
    request,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    inventory_doc = get_user_inventory(user_id)

    if not inventory_doc:
        raise HTTPException(
            status_code=404,
            detail="Inventory document not found"
        )

    items = inventory_doc.get("items", [])

    if (
        request.index < 0
        or request.index >= len(items)
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid item index"
        )

    updated_item = {
        "display_name": request.display_name,
        "quantity": request.quantity,
        "unit": request.unit,
        "category": request.category,
        "purchase_date": request.purchase_date,
        "status": items[request.index].get(
            "status",
            "fresh"
        )
    }

    result = update_inventory_item_by_index(
        user_id,
        request.index,
        updated_item
    )

    if result.modified_count == 0:
        return {
            "message": "No changes made to the item"
        }

    return {
        "message": "Item updated successfully"
    }


def add_inventory_items(
    request,
    background_tasks,
    user_id
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    inventory_doc = get_user_inventory(user_id)

    existing_items = (
        inventory_doc.get("items", [])
        if inventory_doc else []
    )

    new_items = []

    profile = get_profile(user_id)

    household_size = (
        profile.get("household_size", 1)
        if profile else 1
    )

    for item in request.items:
        classified = classify_item(
            item.display_name,
            household_size
        ) or {}

        input_name = item.display_name.strip().lower()

        resolved_name = classified.get(
            "display_name",
            input_name
        )

        for inv_item in existing_items:
            existing_display = inv_item.get(
                "display_name", ""
            ).strip().lower()

            existing_aliases = inv_item.get(
                "aliases", []
            )

            is_duplicate = (
                resolved_name == existing_display
                or input_name == existing_display
                or resolved_name in existing_aliases
                or input_name in existing_aliases
            )

            if is_duplicate:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"You already have "
                        f"{inv_item.get('display_name')}! "
                        f"Please edit the quantity instead."
                    )
                )

        aliases = (
            [input_name]
            if input_name != resolved_name
            else []
        )

        item_dict = {
            "display_name": resolved_name.title(),
            "aliases": aliases,
            "quantity": classified.get(
                "quantity",
                item.quantity
            ),
            "unit": classified.get(
                "unit",
                item.unit
            ),
            "category": classified.get(
                "category",
                "Other"
            ),
            "purchase_date": item.purchase_date,
            "status": "fresh"
        }

        new_items.append(item_dict)

    push_inventory_items(
        user_id,
        new_items
    )

    for item in request.items:
        background_tasks.add_task(
            get_shelf_life,
            item.display_name
        )

    return {
        "message": "Items added successfully",
        "count": len(new_items)
    }


def get_inventory(user_id):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    inventory_doc = get_user_inventory(user_id)

    if not inventory_doc:
        return []

    inventory = inventory_doc.get(
        "items",
        []
    )

    return enrich_with_shelf_life(
        inventory
    )