from datetime import date, datetime, timedelta

from db.collections import (
    inventory_collection,
    profiles_collection,
    meal_plans_collection,
    nutrition_logs_collection,
)

from utils.inventory_utils import enrich_with_shelf_life


def get_notifications(user_id: str) -> list:
    notifications = []
    today = date.today()

    # --- Inventory alerts ---
    inventory_doc = inventory_collection.find_one({"user_id": user_id})
    if inventory_doc:
        items = inventory_doc.get("items", [])
        enriched = enrich_with_shelf_life(items)

        expired_names = []
        expiring_soon = []
        out_of_stock = []

        for item in enriched:
            name = item.get("display_name", "Item")
            try:
                quantity = float(item.get("quantity", 0))
            except (ValueError, TypeError):
                quantity = 0

            purchase_date_str = item.get("purchase_date")
            shelf_life = item.get("shelf_life_days", 7)

            if quantity == 0:
                out_of_stock.append(name)

            if purchase_date_str and quantity > 0:
                try:
                    purchase_date = date.fromisoformat(purchase_date_str)
                    expiry_date = purchase_date + timedelta(days=shelf_life)
                    days_left = (expiry_date - today).days

                    if days_left < 0:
                        expired_names.append(name)
                    elif days_left <= 3:
                        expiring_soon.append((name, days_left))
                except Exception:
                    pass

        if expired_names:
            if len(expired_names) == 1:
                title = f"{expired_names[0]} has expired"
                message = "Remove it from your pantry"
            else:
                title = f"{len(expired_names)} items have expired"
                sample = ", ".join(expired_names[:2])
                message = f"Including {sample}"
            notifications.append({
                "id": "inv_expired",
                "type": "inventory",
                "severity": "danger",
                "title": title,
                "message": message,
                "action_url": "/inventory",
            })

        for name, days in expiring_soon:
            label = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
            notifications.append({
                "id": f"inv_expiring_{name.lower().replace(' ', '_')}",
                "type": "inventory",
                "severity": "warning",
                "title": f"{name} expiring soon",
                "message": f"Expires {label}",
                "action_url": "/inventory",
            })

        if out_of_stock:
            count = len(out_of_stock)
            notifications.append({
                "id": "inv_out_of_stock",
                "type": "shopping",
                "severity": "info",
                "title": "Shopping list needs updating",
                "message": f"{count} item{'s' if count != 1 else ''} {'are' if count != 1 else 'is'} out of stock",
                "action_url": "/inventory",
            })

    # --- Meal plan reminders ---
    meal_doc = meal_plans_collection.find_one({"user_id": user_id})
    if not meal_doc:
        notifications.append({
            "id": "meal_no_plan",
            "type": "meal",
            "severity": "info",
            "title": "No meal plan this week",
            "message": "Start planning your meals for the week",
            "action_url": "/meal-plan",
        })
    else:
        today_name = today.strftime("%A")
        meals_today = meal_doc.get("meals", {}).get(today_name, {})
        has_valid_meal = any(
            any(m.get("valid") for m in slot)
            for slot in meals_today.values()
            if isinstance(slot, list)
        )
        if not has_valid_meal:
            notifications.append({
                "id": "meal_today_empty",
                "type": "meal",
                "severity": "info",
                "title": f"No meals planned for {today_name}",
                "message": "Add meals to your plan for today",
                "action_url": "/meal-plan",
            })

    # --- Nutrition alerts ---
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    recent_log = nutrition_logs_collection.find_one({
        "user_id": user_id,
        "created_at": {"$gte": three_days_ago},
    })

    if not recent_log:
        total_logs = nutrition_logs_collection.count_documents({"user_id": user_id})
        if total_logs == 0:
            notifications.append({
                "id": "nutrition_no_logs",
                "type": "nutrition",
                "severity": "info",
                "title": "Start tracking nutrition",
                "message": "Log your first meal to see nutritional insights",
                "action_url": "/nutrition",
            })
        else:
            notifications.append({
                "id": "nutrition_not_logged",
                "type": "nutrition",
                "severity": "info",
                "title": "Nutrition not logged recently",
                "message": "Keep your nutrition tracking up to date",
                "action_url": "/nutrition",
            })

    # --- Preferences not set up ---
    profile = profiles_collection.find_one({"user_id": user_id})
    if profile:
        missing = []
        if not profile.get("goals"):
            missing.append("health goals")
        if not profile.get("diet"):
            missing.append("diet preference")
        if not profile.get("allergies"):
            missing.append("allergies")

        if missing:
            sample = " & ".join(missing[:2])
            notifications.append({
                "id": "profile_incomplete",
                "type": "profile",
                "severity": "warning",
                "title": "Complete your preferences",
                "message": f"Add your {sample} for better recommendations",
                "action_url": "/profile",
            })

    return notifications
