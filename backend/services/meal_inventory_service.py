from utils.matching_utils import fuzzy_match

from utils.unit_utils import (
    normalize_unit
)


def fuzzy_inventory_match(a, b):
    return fuzzy_match(a, b)


def deduct_ingredients(
    inventory,
    meal_ingredients
):
    updates = {}

    for ing in meal_ingredients:

        for idx, inv_item in enumerate(inventory):

            if fuzzy_match(
                ing["name"],
                inv_item["display_name"]
            ):

                norm_unit = normalize_unit(
                    ing.get("unit", "unit")
                )

                used = (
                    float(ing.get("quantity", 1))
                    if norm_unit == inv_item["unit"]
                    else 1
                )

                new_qty = max(
                    0,
                    float(inv_item["quantity"])
                    - used
                )

                updates[
                    f"items.{idx}.quantity"
                ] = new_qty

                inventory[idx]["quantity"] = new_qty

                break

    return updates