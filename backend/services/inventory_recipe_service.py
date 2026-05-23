from fastapi import HTTPException

from dao.inventory_dao import (
    get_user_inventory,
    update_inventory_fields,
    push_inventory_items
)

from utils.unit_utils import (
    normalize_unit
)

from api.routes.shelf_life import (
    get_shelf_life
)


def use_recipe(
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

    if not inventory_doc:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found"
        )

    inventory = inventory_doc.get(
        "items",
        []
    )

    name_to_idx = {}

    for i, item in enumerate(inventory):
        name = item.get("display_name")

        if name:
            name_to_idx[name.strip().lower()] = i

    def find_inv_idx(name: str):
        key = name.strip().lower()

        if key in name_to_idx:
            return name_to_idx[key]

        for inv_key, idx in name_to_idx.items():
            if key in inv_key or inv_key in key:
                return idx

        return None

    ing_map = {
        ing.name.strip().lower(): ing
        for ing in request.ingredients
    }

    updates = {}

    for have_name in request.have:
        idx = find_inv_idx(have_name)

        if idx is None:
            continue

        inv_item = inventory[idx]

        recipe_ing = ing_map.get(
            have_name.strip().lower()
        )

        if (
            recipe_ing
            and normalize_unit(recipe_ing.unit)
            == inv_item.get("unit")
        ):
            try:
                used = float(recipe_ing.quantity)

            except (ValueError, TypeError):
                used = 1

            new_qty = max(
                0,
                float(inv_item.get("quantity", 0))
                - used
            )

        else:
            new_qty = max(
                0,
                float(inv_item.get("quantity", 0))
                - 1
            )

        updates[f"items.{idx}.quantity"] = new_qty

    existing_names = {
        item.get("display_name").strip().lower()
        for item in inventory
    }

    new_items = []

    for buy_name in request.need_to_buy:
        if buy_name.strip().lower() in existing_names:
            continue

        recipe_ing = ing_map.get(
            buy_name.strip().lower()
        )

        new_items.append({
            "display_name": buy_name,
            "quantity": 0,
            "unit": (
                normalize_unit(recipe_ing.unit)
                if recipe_ing else "unit"
            ),
            "category": "Other",
            "purchase_date": None,
            "status": "fresh"
        })

        if recipe_ing:
            background_tasks.add_task(
                get_shelf_life,
                buy_name
            )

    if updates:
        update_inventory_fields(
            user_id,
            updates
        )

    if new_items:
        push_inventory_items(
            user_id,
            new_items
        )

    return {
        "message": "Inventory updated",
        "adjusted": len(updates),
        "added": len(new_items)
    }