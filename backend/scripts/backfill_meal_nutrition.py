"""
Backfill nutrition data on meal plan entries where the valid entry has an empty
nutrition dict — caused by meals added via the chatbot before the threading fix.

Run from the backend directory:
    python -m scripts.backfill_meal_nutrition
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.collections import meal_plans_collection
from services.nutrition_service import store_nutrition_nested


def backfill_meal_nutrition():
    plans = list(meal_plans_collection.find({}))
    print(f"Meal plan documents found: {len(plans)}")

    fetched = 0
    skipped = 0

    for plan in plans:
        user_id = plan.get("user_id", "")
        if not user_id:
            continue

        meals = plan.get("meals", {})

        for day, slots in meals.items():
            for meal_type, entries in slots.items():
                if not isinstance(entries, list):
                    continue

                valid_entry = next(
                    (e for e in reversed(entries) if e.get("valid") is True),
                    None,
                )

                if valid_entry is None:
                    continue

                if valid_entry.get("nutrition"):
                    skipped += 1
                    continue

                meal_name = valid_entry.get("meal_name", "")
                if not meal_name:
                    continue

                print(f"  {user_id} | {day} {meal_type} | '{meal_name}'")
                try:
                    store_nutrition_nested(user_id, day, meal_type, meal_name)
                    fetched += 1
                except Exception as e:
                    print(f"    Error: {e}")

    print(f"\nDone. Fetched nutrition for {fetched} entries, skipped {skipped} already populated.")


if __name__ == "__main__":
    backfill_meal_nutrition()
