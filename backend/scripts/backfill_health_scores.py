"""
Backfill health_score on existing nutrition logs and meal plan entries.

Run from the backend directory:
    python -m scripts.backfill_health_scores
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.collections import nutrition_logs_collection, meal_plans_collection, profiles_collection
from services.health_score_service import calculate_meal_health_score
from services.nutrition_target_service import get_daily_targets
from utils.datetime_utils import now_utc


_targets_cache: dict = {}

def _get_daily_targets_for_user(user_id: str) -> dict:
    if user_id not in _targets_cache:
        profile = profiles_collection.find_one({"user_id": user_id})
        goals = profile.get("goals", []) if profile else []
        _targets_cache[user_id] = get_daily_targets(goals)
    return _targets_cache[user_id]


# ── 1. Nutrition logs ─────────────────────────────────────────────────────────

def backfill_nutrition_logs():
    query = {"health_score": {"$exists": False}}
    logs = list(nutrition_logs_collection.find(query))
    print(f"Nutrition logs missing health_score: {len(logs)}")

    updated = 0
    for log in logs:
        try:
            targets = _get_daily_targets_for_user(log["user_id"])
            score = calculate_meal_health_score(
                meal_name=log.get("meal", ""),
                nutrition=log.get("nutrition") or {},
                meal_type=log.get("meal_type", "dinner"),
                created_at=log.get("created_at", now_utc()),
                daily_targets=targets,
            )
            nutrition_logs_collection.update_one(
                {"_id": log["_id"]},
                {"$set": {"health_score": score}},
            )
            updated += 1
        except Exception as e:
            print(f"  Skipped log {log['_id']}: {e}")

    print(f"  Updated {updated} nutrition logs.\n")


# ── 2. Meal plan entries ──────────────────────────────────────────────────────

def backfill_meal_plans():
    plans = list(meal_plans_collection.find({}))
    print(f"Meal plan documents: {len(plans)}")

    updated_docs = 0
    updated_entries = 0

    for plan in plans:
        user_id = plan.get("user_id", "")
        meals = plan.get("meals", {})
        changed = False

        try:
            targets = _get_daily_targets_for_user(user_id)
        except Exception as e:
            print(f"  Skipped plan for user {user_id}: {e}")
            continue

        for day, slots in meals.items():
            for meal_type, entries in slots.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if "health_score" in entry:
                        continue
                    nutrition = entry.get("nutrition") or {}
                    if not nutrition:
                        continue
                    try:
                        created_at = entry.get("created_at") or plan.get("created_at") or now_utc()
                        score = calculate_meal_health_score(
                            meal_name=entry.get("meal_name", ""),
                            nutrition=nutrition,
                            meal_type=meal_type,
                            created_at=created_at,
                            daily_targets=targets,
                        )
                        entry["health_score"] = score
                        changed = True
                        updated_entries += 1
                    except Exception as e:
                        print(f"  Skipped entry '{entry.get('meal_name')}': {e}")

        if changed:
            meal_plans_collection.update_one(
                {"_id": plan["_id"]},
                {"$set": {"meals": meals}},
            )
            updated_docs += 1

    print(f"  Updated {updated_entries} meal entries across {updated_docs} meal plan documents.\n")


if __name__ == "__main__":
    backfill_nutrition_logs()
    backfill_meal_plans()
    print("Done.")
