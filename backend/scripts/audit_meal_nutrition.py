"""
Audit nutrition data for every meal in the DB.

Shows each meal's current calories/macros (or marks it as MISSING).
Pass --fix to automatically fetch nutrition for any meal with an empty dict.

Run from the backend directory:
    python -m scripts.audit_meal_nutrition          # report only
    python -m scripts.audit_meal_nutrition --fix    # report + backfill missing
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.collections import meal_plans_collection
from services.nutrition_service import store_nutrition_nested


MACRO_KEYS = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]


def fmt_nutrition(nutrition: dict) -> str:
    if not nutrition:
        return "*** MISSING ***"
    parts = [f"{k.replace('_g','').replace('_mg','')}: {nutrition.get(k, 0)}" for k in MACRO_KEYS]
    return "  |  ".join(parts)


def audit(fix: bool = False):
    plans = list(meal_plans_collection.find({}))
    print(f"Found {len(plans)} meal plan document(s)\n")

    total = 0
    missing = []

    for plan in plans:
        user_id = plan.get("user_id", "unknown")
        meals = plan.get("meals", {})

        if not meals:
            continue

        print(f"{'='*70}")
        print(f"User: {user_id}")
        print(f"{'='*70}")

        for day in sorted(meals.keys()):
            slots = meals[day]
            for meal_type, entries in slots.items():
                if not isinstance(entries, list):
                    continue

                valid_entry = next(
                    (e for e in reversed(entries) if e.get("valid") is True),
                    None,
                )

                if valid_entry is None:
                    continue

                total += 1
                meal_name = valid_entry.get("meal_name", "(no name)")
                nutrition = valid_entry.get("nutrition") or {}

                status = fmt_nutrition(nutrition)
                print(f"  [{day}] {meal_type:<12} | {meal_name:<35} | {status}")

                if not nutrition:
                    missing.append((user_id, day, meal_type, meal_name))

        print()

    print(f"Summary: {total} meals total, {len(missing)} missing nutrition\n")

    if not missing:
        print("Nothing to fix.")
        return

    if not fix:
        print("Run with --fix to fetch nutrition for the meals above.")
        return

    print(f"Fetching nutrition for {len(missing)} meals...\n")
    success = 0
    for user_id, day, meal_type, meal_name in missing:
        print(f"  Fetching: [{day}] {meal_type} | '{meal_name}' ...")
        try:
            store_nutrition_nested(user_id, day, meal_type, meal_name)
            print(f"    Done.")
            success += 1
        except Exception as e:
            print(f"    Error: {e}")

    print(f"\nFinished. Populated {success}/{len(missing)} meals.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and optionally fix missing meal nutrition.")
    parser.add_argument("--fix", action="store_true", help="Fetch and store nutrition for meals with empty data")
    args = parser.parse_args()

    audit(fix=args.fix)
