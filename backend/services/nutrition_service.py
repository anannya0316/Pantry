from dao.meal_dao import (
    get_meal_plan,
    update_meal_plan
)

from utils.datetime_utils import (
    now_utc
)

import json

from utils.prompt_loader import load_prompt
from utils.llm_client import get_api_key, call_llm


def fetch_nutrition(
    meal_name: str
):
    if not get_api_key():
        return {}

    prompt_template = load_prompt(
    "nutrition.txt"
    )

    prompt = prompt_template.format(
    meal_name=meal_name
    )

    try:

        content = call_llm(
            prompt,
            temperature=0,
            timeout=20,
        )

        if content.startswith("```"):

            content = content.split(
                "```"
            )[1]

            if content.startswith("json"):
                content = content[4:]

            content = content.strip()

        parsed = json.loads(content)

        return {
            "calories":
                float(parsed.get(
                    "calories",
                    0
                )),

            "protein_g":
                float(parsed.get(
                    "protein_g",
                    0
                )),

            "carbs_g":
                float(parsed.get(
                    "carbs_g",
                    0
                )),

            "fat_g":
                float(parsed.get(
                    "fat_g",
                    0
                )),

            "fiber_g":
                float(parsed.get(
                    "fiber_g",
                    0
                )),

            "vitamin_c_mg":
                float(parsed.get(
                    "vitamin_c_mg",
                    0
                )),

            "iron_mg":
                float(parsed.get(
                    "iron_mg",
                    0
                )),

            "calcium_mg":
                float(parsed.get(
                    "calcium_mg",
                    0
                )),
        }

    except Exception as exc:

        print(
            f"fetch_nutrition error: "
            f"{exc}"
        )

        return {}


def store_nutrition_nested(
    user_id,
    day,
    meal_type,
    meal_name
):
    nutrition = fetch_nutrition(meal_name)

    if not nutrition:
        return

    meal_doc = get_meal_plan(user_id)

    if not meal_doc:
        return

    meals = meal_doc.get("meals", {})

    slot_meals = meals.get(
        day,
        {}
    ).get(
        meal_type,
        []
    )

    for meal in reversed(slot_meals):

        if meal.get("valid") is True:

            meal["nutrition"] = nutrition

            meal["updated_at"] = now_utc()

            break

    update_meal_plan(
        user_id,
        meals,
        now_utc()
    )