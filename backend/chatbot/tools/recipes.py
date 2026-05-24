import json
import logging

from dao.inventory_dao import get_user_inventory, get_profile
from utils.prompt_loader import load_prompt
from utils.llm_client import get_api_key, call_llm

logger = logging.getLogger("pantry.agent")


def suggest_recipes(user_id: str, preferences: str = None) -> dict:
    if not get_api_key():
        logger.error("suggest_recipes: OPEN_ROUTER_KEY not set")
        return {"success": False, "error": "Recipe service unavailable (no API key)."}

    inventory_doc = get_user_inventory(user_id)
    if not inventory_doc:
        return {"success": False, "error": "No inventory found."}

    items = [i for i in inventory_doc.get("items", []) if (i.get("quantity") or 0) > 0]
    if not items:
        return {"success": False, "error": "Your inventory is empty — add some ingredients first."}

    profile = get_profile(user_id) or {}
    household_size = profile.get("household_size", 2)

    inventory_lines = "\n".join(
        f"- {item['display_name']}: {item['quantity']} {item['unit']}"
        for item in items
    )

    preferences_line = f"Special request: {preferences}" if preferences else ""

    profile_parts = []
    if profile.get("diet"):
        profile_parts.append(f"Diet: {profile['diet']}")
    if profile.get("allergies"):
        profile_parts.append(f"Allergies/intolerances: {', '.join(profile['allergies'])}")
    if profile.get("spice_preference"):
        profile_parts.append(f"Spice preference: {profile['spice_preference']}")
    if profile.get("favorite_cuisines"):
        profile_parts.append(f"Favorite cuisines: {', '.join(profile['favorite_cuisines'])}")
    if profile.get("liked_ingredients"):
        profile_parts.append(f"Liked ingredients: {', '.join(profile['liked_ingredients'])}")
    if profile.get("disliked_ingredients"):
        profile_parts.append(f"Disliked ingredients: {', '.join(profile['disliked_ingredients'])}")
    if profile.get("goals"):
        profile_parts.append(f"Health goals: {', '.join(profile['goals'])}")
    profile_context = "\n".join(profile_parts)

    try:
        prompt = load_prompt("recipe_suggestion.txt").format(
            inventory=inventory_lines,
            household_size=household_size,
            preferences_line=preferences_line,
            profile_context=profile_context,
        )

        content = call_llm(prompt, temperature=0.3, timeout=30, max_tokens=900)
        logger.info(f"suggest_recipes: raw LLM response (first 200 chars): {content[:200]}")

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        recipes = json.loads(content)

        if not isinstance(recipes, list):
            return {"success": False, "error": "Unexpected response format from LLM."}

        return {"success": True, "recipes": recipes}

    except json.JSONDecodeError as e:
        logger.error(f"suggest_recipes: JSON parse error — {e}")
        return {"success": False, "error": f"LLM returned invalid JSON (possibly truncated): {str(e)}"}
    except Exception as e:
        logger.error(f"suggest_recipes: unexpected error — {type(e).__name__}: {e}")
        return {"success": False, "error": f"Recipe generation failed: {type(e).__name__}: {str(e)}"}
