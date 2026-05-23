from pydantic import BaseModel

from dao.inventory_dao import get_user_inventory
from dao.profile_dao import get_profile
from chatbot.tools.meal_plan import get_meal_plan_item as get_meal_plan


# ── Pydantic schema ───────────────────────────────────────────────────────────

class GetShoppingListInput(BaseModel):
    pass

_LOW_STOCK_THRESHOLDS = {
    "pieces": 2,
    "unit":   2,
    "dozen":  0.5,
    "kg":     0.5,
    "g":      200,
    "liter":  0.5,
    "liters": 0.5,
    "ml":     250,
    "lbs":    0.5,
    "loaf":   1,
}


def _is_low(quantity: float, unit: str) -> bool:
    threshold = _LOW_STOCK_THRESHOLDS.get(unit.lower(), 1)
    return 0 < quantity < threshold


def get_shopping_list(user_id: str) -> dict:
    try:
        profile = get_profile(user_id) or {}
        household_size = profile.get("household_size", 1) or 1

        # ── Inventory ──────────────────────────────────────────────
        inventory_doc = get_user_inventory(user_id) or {"items": []}
        items = inventory_doc.get("items", [])

        out_of_stock = []
        expired      = []
        low_stock    = []

        for item in items:
            name     = item.get("display_name", "Unknown")
            quantity = item.get("quantity", 0) or 0
            unit     = (item.get("unit") or "unit").lower()
            status   = (item.get("status") or "fresh").lower()

            if status == "expired":
                expired.append({"name": name, "reason": "expired"})
            elif quantity == 0 or status == "consumed":
                out_of_stock.append({"name": name, "reason": "out of stock"})
            elif _is_low(quantity, unit):
                low_stock.append({
                    "name":     name,
                    "quantity": quantity,
                    "unit":     unit,
                    "reason":   "low stock",
                })

        # ── Meal-plan ingredients ───────────────────────────────────
        plan_result = get_meal_plan(user_id=user_id)
        needed_for_plan = []

        if plan_result.get("success"):
            existing = {i.get("display_name", "").lower() for i in items}
            meals_by_day = (plan_result.get("data") or {}).get("meals", {})

            seen_ingredients: set[str] = set()
            for day, slots in meals_by_day.items():
                for meal_type, entries in slots.items():
                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        if entry.get("consumed"):
                            continue
                        meal_name   = entry.get("meal_name", "planned meal")
                        ingredients = entry.get("ingredients") or []
                        for ing in ingredients:
                            if isinstance(ing, str):
                                ing_name, ing_qty, ing_unit = ing, None, None
                            else:
                                ing_name = ing.get("name", "")
                                ing_qty  = ing.get("quantity")
                                ing_unit = ing.get("unit")
                            if not ing_name:
                                continue
                            key = ing_name.lower()
                            if key not in existing and key not in seen_ingredients:
                                seen_ingredients.add(key)
                                entry: dict = {
                                    "name":       ing_name,
                                    "reason":     "needed for meal plan",
                                    "needed_for": f"{meal_name} ({day} {meal_type})",
                                }
                                if ing_qty and ing_unit:
                                    total = round(ing_qty * household_size, 2)
                                    entry["suggested_quantity"] = total
                                    entry["unit"] = ing_unit
                                needed_for_plan.append(entry)

        shopping_list = out_of_stock + expired + low_stock + needed_for_plan

        def _bullets(items_iter) -> str:
            return "\n".join(f"• {i}" for i in items_iter)

        sections = []
        if out_of_stock:
            sections.append("**Out of stock:**\n" + _bullets(i["name"] for i in out_of_stock))
        if expired:
            sections.append("**Expired (replace):**\n" + _bullets(i["name"] for i in expired))
        if low_stock:
            sections.append("**Running low:**\n" + _bullets(
                f"{i['name']} ({i['quantity']} {i['unit']} left)" for i in low_stock
            ))
        if needed_for_plan:
            sections.append("**Needed for meal plan:**\n" + _bullets(i["name"] for i in needed_for_plan))

        if sections:
            message = "Here's your shopping list:\n\n" + "\n\n".join(sections)
        else:
            message = "Your pantry looks fully stocked! Nothing to buy right now."

        return {
            "success": True,
            "message": message,
            "shopping_list": shopping_list,
            "household_size": household_size,
            "summary": {
                "out_of_stock":         len(out_of_stock),
                "expired":              len(expired),
                "low_stock":            len(low_stock),
                "needed_for_meal_plan": len(needed_for_plan),
                "total":                len(shopping_list),
            },
        }

    except Exception as e:
        import traceback
        print(f"get_shopping_list error: {e!r}\n{traceback.format_exc()}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
