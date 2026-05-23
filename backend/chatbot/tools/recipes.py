import json

from dao.inventory_dao import get_user_inventory, get_profile
from utils.prompt_loader import load_prompt
from utils.llm_client import get_api_key, call_llm


def suggest_recipes(user_id: str, preferences: str = None) -> dict:
    if not get_api_key():
        return {"success": False, "error": "Recipe service unavailable."}

    inventory_doc = get_user_inventory(user_id)
    if not inventory_doc:
        return {"success": False, "error": "No inventory found."}

    items = [i for i in inventory_doc.get("items", []) if (i.get("quantity") or 0) > 0]
    if not items:
        return {"success": False, "error": "Your inventory is empty — add some ingredients first."}

    profile = get_profile(user_id)
    household_size = profile.get("household_size", 2) if profile else 2

    inventory_lines = "\n".join(
        f"- {item['display_name']}: {item['quantity']} {item['unit']}"
        for item in items
    )

    preferences_line = f"User preferences: {preferences}" if preferences else ""

    prompt = load_prompt("recipe_suggestion.txt").format(
        inventory=inventory_lines,
        household_size=household_size,
        preferences_line=preferences_line,
    )

    try:
        content = call_llm(prompt, temperature=0.3, timeout=20)

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        recipes = json.loads(content)

        if not isinstance(recipes, list):
            return {"success": False, "error": "Unexpected response format."}

        return {"success": True, "recipes": recipes}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
