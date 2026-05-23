import json
from datetime import date, timedelta

from utils.prompt_loader import load_prompt
from utils.llm_client import get_api_key, call_llm
from dao.inventory_dao import (
    get_user_inventory,
    get_profile
)


WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]


def days_until(target_weekday: str) -> int:
    today_idx = date.today().weekday()
    target_idx = WEEKDAYS.index(target_weekday)
    delta = (target_idx - today_idx) % 7
    return delta if delta > 0 else 7


def get_low_stock_items(user_id: str) -> list:
    if not get_api_key():
        return []

    inventory_doc = get_user_inventory(user_id)
    profile = get_profile(user_id)

    if not inventory_doc or not profile:
        return []

    items = inventory_doc.get("items", [])

    if not items:
        return []

    household_size = profile.get("household_size", 2)
    shopping_day = profile.get("grocery_shopping_day", "Sunday")
    days_until_shopping = days_until(shopping_day)

    inventory_summary = [
        {
            "display_name": item.get("display_name"),
            "quantity": item.get("quantity"),
            "unit": item.get("unit"),
        }
        for item in items
        if (item.get("quantity") or 0) != 0
    ]

    prompt_template = load_prompt("low_stock.txt")

    prompt = prompt_template.format(
        today=date.today().isoformat(),
        household_size=household_size,
        grocery_shopping_day=shopping_day,
        days_until_shopping=days_until_shopping,
        inventory_json=json.dumps(inventory_summary, indent=2)
    )

    try:
        content = call_llm(prompt, temperature=0, timeout=15)

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)

        if not isinstance(result, list):
            return []

        return result

    except Exception as e:
        print(f"[low_stock] error: {e}")
        return []
