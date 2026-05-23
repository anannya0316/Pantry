from datetime import datetime, timezone

from db.collections import agent_events_collection, nutrition_logs_collection


def record_meal_event(user_id: str, dish: str, meal_type: str, day: str) -> None:
    agent_events_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "event_type": "meal_logged",
        "payload": {"dish": dish, "meal_type": meal_type, "day": day},
    })


def get_recent_context(user_id: str, limit: int = 5) -> str:
    """Return a short natural-language summary of recent meal events for the system prompt."""
    events = list(
        agent_events_collection
        .find({"user_id": user_id, "event_type": "meal_logged"}, {"_id": 0, "payload": 1})
        .sort("timestamp", -1)
        .limit(limit)
    )
    if not events:
        return ""

    lines = [
        f"- {e['payload']['dish']} ({e['payload']['meal_type']})"
        for e in events
        if e.get("payload")
    ]
    return "Recently logged meals:\n" + "\n".join(lines)


def get_top_meals(user_id: str, per_type_limit: int = 2) -> str:
    """Return the most frequently logged meals per meal type over the last 30 days."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    pipeline = [
        {"$match": {"user_id": user_id, "created_at": {"$gte": cutoff}}},
        {"$group": {"_id": {"meal": "$meal", "meal_type": "$meal_type"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    results = list(nutrition_logs_collection.aggregate(pipeline))
    if not results:
        return ""

    by_type: dict[str, list[str]] = {}
    for r in results:
        mt = r["_id"]["meal_type"]
        meal = r["_id"]["meal"]
        by_type.setdefault(mt, [])
        if len(by_type[mt]) < per_type_limit:
            by_type[mt].append(meal)

    lines = []
    for mt in ("breakfast", "lunch", "dinner"):
        if mt in by_type:
            lines.append(f"{mt}: {', '.join(by_type[mt])}")

    return "Frequently logged meals:\n" + "\n".join(lines) if lines else ""
