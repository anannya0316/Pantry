import json

from constants.meal_constants import (
    VALID_UNITS
)
from utils.prompt_loader import load_prompt
from utils.web_search import tavily_search
from utils.llm_client import get_api_key, call_llm


def _call_llm(
    prompt: str,
    label: str = "",
) -> list:
    try:
        content = call_llm(prompt, temperature=0, timeout=15)
    except Exception as e:
        print(
            f"[ingredients{label}] LLM error: {e}"
        )
        return []

    print(f"[ingredients{label}] raw response: {content[:300]}")

    # Strip markdown fences
    if "```" in content:
        parts = content.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
            if stripped.startswith("[") or stripped.startswith("{"):
                content = stripped
                break

    # Extract first [...] block in case of surrounding text
    start = content.find("[")
    end = content.rfind("]")

    if start != -1 and end != -1 and end > start:
        content = content[start:end + 1]

    result = json.loads(content)

    # Unwrap object wrapper e.g. {"ingredients": [...]}
    if isinstance(result, dict):
        for val in result.values():
            if isinstance(val, list):
                result = val
                break
        else:
            return []

    if not isinstance(result, list):
        return []

    cleaned = []

    for item in result:
        unit = item.get("unit", "unit")

        if unit not in VALID_UNITS:
            unit = "unit"

        try:
            qty = float(item.get("quantity", 1))
        except (ValueError, TypeError):
            qty = 1

        cleaned.append({
            "name": item["name"],
            "quantity": qty,
            "unit": unit
        })

    return cleaned


def _build_pref_str(preferences: dict) -> str:
    lines = []

    diet = preferences.get("diet")
    if diet:
        val = ", ".join(diet) if isinstance(diet, list) else diet
        lines.append(f"Diet: {val}")

    allergies = preferences.get("allergies")
    if allergies:
        lines.append(f"Allergies (must avoid): {', '.join(allergies)}")

    spice = preferences.get("spice_preference")
    if spice:
        lines.append(f"Spice preference: {spice}")

    liked = preferences.get("liked_ingredients")
    if liked:
        lines.append(f"Liked ingredients: {', '.join(liked)}")

    disliked = preferences.get("disliked_ingredients")
    if disliked:
        lines.append(f"Disliked ingredients: {', '.join(disliked)}")

    cuisines = preferences.get("favorite_cuisines")
    if cuisines:
        lines.append(f"Favourite cuisines: {', '.join(cuisines)}")

    special = preferences.get("special_preferences")
    if special:
        lines.append(f"Special preferences: {', '.join(special)}")

    return "\n".join(lines) if lines else "none"


def _fetch_for_single_meal(
    meal_name: str,
    household_size: int,
    pref_str: str,
    prompt_template: str,
) -> list:
    print(f"[ingredients] fetching for '{meal_name}'")

    prompt = prompt_template.format(
        meal_name=meal_name,
        household_size=household_size,
        pref_str=pref_str,
        web_context="",
    )

    result = _call_llm(prompt, label=f" '{meal_name}'")

    if result:
        print(
            f"[ingredients] got {len(result)} items"
            f" for '{meal_name}' (no web search needed)"
        )
        return result

    print(
        f"[ingredients] LLM returned empty for '{meal_name}',"
        " trying web search fallback"
    )

    web_context = tavily_search(
        f"{meal_name} recipe ingredients Indian"
    )

    if not web_context:
        print(f"[ingredients] web search also returned nothing for '{meal_name}'")
        return []

    context_block = f"\nWeb search context:\n{web_context}\n"

    prompt = prompt_template.format(
        meal_name=meal_name,
        household_size=household_size,
        pref_str=pref_str,
        web_context=context_block,
    )

    result = _call_llm(prompt, label=f" '{meal_name}' (web)")

    print(
        f"[ingredients] web fallback got {len(result)} items"
        f" for '{meal_name}'"
    )

    return result


def fetch_ingredients(
    meal_name: str,
    household_size: int,
    preferences: dict = None,
) -> list:

    if not get_api_key():
        return []

    pref_str = _build_pref_str(preferences or {})
    prompt_template = load_prompt("ingredient_extraction.txt")

    components = [
        part.strip()
        for part in meal_name.split(" and ")
        if part.strip()
    ]

    all_ingredients = []

    for component in components:
        try:
            results = _fetch_for_single_meal(
                component,
                household_size,
                pref_str,
                prompt_template,
            )
            all_ingredients.extend(results)
        except Exception as e:
            print(
                f"[meal_plan] ingredient fetch error"
                f" for '{component}': {e}"
            )

    return all_ingredients
