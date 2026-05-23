from datetime import (
    datetime,
    timedelta,
    date as date_type,
)

from fastapi import HTTPException

from constants.nutrition_constants import (
    DAY_NAMES
)

from dao.meal_dao import (
    get_meal_plan
)

from dao.nutrition_dao import (
    get_nutrition_logs,
    get_profile
)

from services.nutrition_target_service import (
    get_daily_targets
)

from utils.nutrition_utils import (
    sum_nutrition,
    get_all_consumed_meals,
)

from jobs.auto_consume import (
    auto_consume_past_meals
)

from utils.datetime_utils import (
    now_ist,
    to_ist
)


def _parse_log_date(log):
    created = log.get("created_at")
    if created is None:
        return None
    try:
        if isinstance(created, str):
            dt = datetime.fromisoformat(created)
            if dt.tzinfo is None:
                from datetime import timezone
                dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = created
        return to_ist(dt).date()
    except Exception:
        return None


def get_nutrition_insights(
    user_id: str,
    period: str = "weekly"
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header required"
        )

    user = get_profile(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    goals = user.get("goals", [])

    DAILY_TARGETS = get_daily_targets(goals)

    ist_now = now_ist()
    today = ist_now.date()
    today_name = DAY_NAMES[today.weekday()]

    auto_consume_past_meals(user_id, today)

    monday_of_week = today - timedelta(days=today.weekday())

    if period == "monthly":
        start_date = today.replace(day=1)
    else:
        start_date = monday_of_week

    week_dates = {
        DAY_NAMES[i]: (
            monday_of_week + timedelta(days=i)
        ).isoformat()
        for i in range(7)
    }

    meal_doc = get_meal_plan(user_id)

    all_active_meals = (
        get_all_consumed_meals(meal_doc)
        if meal_doc else []
    )

    all_logs = get_nutrition_logs(user_id)

    # Group logs in range by date and track covered day/meal_type pairs
    logs_by_date = {}
    covered_slots = set()  # {(date_str, meal_type)} for dedup

    for log in all_logs:
        log_date = _parse_log_date(log)

        if log_date is None:
            continue

        if not (start_date <= log_date <= today):
            continue

        date_key = log_date.isoformat()

        logs_by_date.setdefault(date_key, []).append(log)

        mt = log.get("meal_type")

        if mt in ("breakfast", "lunch", "dinner"):
            covered_slots.add((date_key, mt))

    # Consumed meal plan meals de-duplicated against nutrition logs.
    # Only count consumed=True meals whose slot is not already covered
    # by a nutrition log entry.
    meals_by_day = {}

    for meal in all_active_meals:

        day = meal.get("day")
        meal_type = meal.get("meal_type")

        if not day or not meal_type:
            continue

        day_date_str = week_dates.get(day)

        if not day_date_str:
            continue

        try:
            day_date_obj = date_type.fromisoformat(
                day_date_str
            )
        except Exception:
            continue

        if not (start_date <= day_date_obj <= today):
            continue

        if meal_type in ("breakfast", "lunch", "dinner"):
            if (day_date_str, meal_type) in covered_slots:
                continue

        meals_by_day.setdefault(day, []).append(meal)

    # Build calorie trend
    if period == "weekly":
        trend = []

        for day_name in DAY_NAMES:
            day_date = week_dates[day_name]

            if date_type.fromisoformat(day_date) > today:
                break

            calories = sum(
                m.get("nutrition", {}).get("calories", 0)
                for m in meals_by_day.get(day_name, [])
            )

            calories += sum(
                log.get("nutrition", {}).get("calories", 0)
                for log in logs_by_date.get(day_date, [])
            )

            trend.append({
                "day": day_name[:3],
                "calories": round(calories)
            })

    else:
        trend = []
        d = start_date
        week_num = 1

        while d <= today:
            week_end = min(
                d + timedelta(days=6),
                today
            )

            week_days = [
                d + timedelta(days=i)
                for i in range((week_end - d).days + 1)
            ]

            total_cals = 0
            days_with_data = 0

            for wd in week_days:
                wd_str = wd.isoformat()
                wd_name = DAY_NAMES[wd.weekday()]

                day_cals = 0

                if wd >= monday_of_week:
                    day_cals += sum(
                        m.get("nutrition", {}).get("calories", 0)
                        for m in meals_by_day.get(wd_name, [])
                    )

                day_cals += sum(
                    log.get("nutrition", {}).get("calories", 0)
                    for log in logs_by_date.get(wd_str, [])
                )

                if day_cals > 0:
                    days_with_data += 1
                    total_cals += day_cals

            trend.append({
                "day": f"W{week_num}",
                "calories": round(
                    total_cals / max(days_with_data, 1)
                ) if days_with_data else 0
            })

            d += timedelta(days=7)
            week_num += 1

    # Today's macros (always current day, regardless of period)
    today_items = (
        meals_by_day.get(today_name, [])
        + logs_by_date.get(today.isoformat(), [])
    )

    today_sum = sum_nutrition(today_items)

    today_macros = {
        key: {
            "current": round(today_sum[key]),
            "target": round(DAILY_TARGETS[key])
        }
        for key in (
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "fiber_g"
        )
    }

    # Per-day calorie list for avg calculation
    all_date_strs = set()

    if period == "weekly":
        all_date_strs = set(week_dates.values())
    else:
        d = start_date
        while d <= today:
            all_date_strs.add(d.isoformat())
            d += timedelta(days=1)

    daily_cals = []

    for date_str in sorted(all_date_strs):
        try:
            d_obj = date_type.fromisoformat(date_str)
        except Exception:
            continue

        if d_obj > today:
            continue

        d_name = DAY_NAMES[d_obj.weekday()]

        calories = 0

        if d_obj >= monday_of_week:
            calories += sum(
                m.get("nutrition", {}).get("calories", 0)
                for m in meals_by_day.get(d_name, [])
            )

        calories += sum(
            log.get("nutrition", {}).get("calories", 0)
            for log in logs_by_date.get(date_str, [])
        )

        if calories > 0:
            daily_cals.append(calories)

    avg_calories = (
        round(sum(daily_cals) / len(daily_cals))
        if daily_cals else 0
    )

    # Streak: consecutive days with consumed data going backwards from today
    streak = 0
    max_lookback = (today - start_date).days + 1

    for i in range(max_lookback):
        check_date = today - timedelta(days=i)

        if check_date < start_date:
            break

        check_str = check_date.isoformat()
        check_name = DAY_NAMES[check_date.weekday()]

        has_data = bool(logs_by_date.get(check_str))

        if not has_data and check_date >= monday_of_week:
            has_data = bool(meals_by_day.get(check_name))

        if has_data:
            streak += 1
        else:
            break

    # Meals logged count
    consumed_meal_plan_count = sum(
        len(v) for v in meals_by_day.values()
    )

    nutrition_log_count = sum(
        len(v) for v in logs_by_date.values()
    )

    meals_logged = consumed_meal_plan_count + nutrition_log_count

    # Range-wide totals for macros
    all_range_meals = [
        m
        for day_meals in meals_by_day.values()
        for m in day_meals
    ]

    all_range_logs = [
        log
        for day_logs in logs_by_date.values()
        for log in day_logs
    ]

    range_totals = sum_nutrition(
        all_range_meals + all_range_logs
    )

    n_days = max(len(daily_cals), 1)

    protein_calories = range_totals["protein_g"] * 4
    carbs_calories = range_totals["carbs_g"] * 4
    fat_calories = range_totals["fat_g"] * 9
    macro_total = (
        protein_calories + carbs_calories + fat_calories
        or 1
    )

    macro_distribution = {
        "protein_pct": round(
            protein_calories / macro_total * 100
        ),
        "carbs_pct": round(
            carbs_calories / macro_total * 100
        ),
        "fat_pct": round(
            fat_calories / macro_total * 100
        ),
    }

    nutrient_goals = [
        {
            "name": "Protein",
            "current": round(
                range_totals["protein_g"] / n_days
            ),
            "goal": int(DAILY_TARGETS["protein_g"]),
            "unit": "g"
        },
        {
            "name": "Fiber",
            "current": round(
                range_totals["fiber_g"] / n_days
            ),
            "goal": int(DAILY_TARGETS["fiber_g"]),
            "unit": "g"
        },
        {
            "name": "Vitamin C",
            "current": round(
                range_totals["vitamin_c_mg"] / n_days
            ),
            "goal": int(DAILY_TARGETS["vitamin_c_mg"]),
            "unit": "mg"
        },
        {
            "name": "Iron",
            "current": round(
                range_totals["iron_mg"] / n_days
            ),
            "goal": int(DAILY_TARGETS["iron_mg"]),
            "unit": "mg"
        },
        {
            "name": "Calcium",
            "current": round(
                range_totals["calcium_mg"] / n_days
            ),
            "goal": int(DAILY_TARGETS["calcium_mg"]),
            "unit": "mg"
        },
    ]

    macro_check_keys = (
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g"
    )

    range_avg = {
        key: range_totals.get(key, 0) / n_days
        for key in macro_check_keys
    }

    if any(v > 0 for v in range_avg.values()):
        adherence = [
            min(
                range_avg[key] / DAILY_TARGETS[key],
                1.0
            )
            for key in macro_check_keys
        ]

        nutrition_goals_pct = round(
            sum(adherence) / len(adherence) * 100
        )

    else:
        nutrition_goals_pct = 0

    period_label = "week" if period == "weekly" else "month"

    days_so_far = (today - start_date).days + 1
    avg_meals_per_day = meals_logged / max(days_so_far, 1)

    if avg_meals_per_day >= 3:
        meal_consistency = "Excellent"
        consistency_sub = (
            f"Logged {meals_logged} meals this {period_label}"
        )
    elif avg_meals_per_day >= 2:
        meal_consistency = "Good"
        consistency_sub = (
            f"Logged {meals_logged} meals this {period_label}"
        )
    else:
        meal_consistency = "Needs Work"
        consistency_sub = (
            f"Only {meals_logged} meals logged"
            f" this {period_label}"
        )

    all_scores = [
        item["health_score"]
        for item in all_range_meals + all_range_logs
        if isinstance(item.get("health_score"), (int, float))
    ]

    health_score = (
        round(sum(all_scores) / len(all_scores))
        if all_scores else 0
    )

    protein_pct = macro_distribution["protein_pct"]
    carbs_pct = macro_distribution["carbs_pct"]
    fat_pct = macro_distribution["fat_pct"]

    if protein_pct + carbs_pct + fat_pct > 0:
        protein_score = max(
            0, 1 - abs(protein_pct - 30) / 30
        )
        carbs_score = max(
            0, 1 - abs(carbs_pct - 50) / 50
        )
        fat_score = max(
            0, 1 - abs(fat_pct - 27) / 27
        )

        diet_balance_pct = round(
            (protein_score + carbs_score + fat_score)
            / 3 * 100
        )

    else:
        diet_balance_pct = 0

    goals_sub = (
        f"{'Weekly' if period == 'weekly' else 'Monthly'}"
        " average across calories, protein, carbs & fat"
    )

    return {
        "streak": streak,
        "avg_calories": avg_calories,
        "meals_logged": meals_logged,
        "health_score": health_score,
        "weekly_trend": trend,
        "today_macros": today_macros,
        "macro_distribution": macro_distribution,
        "nutrient_goals": nutrient_goals,
        "nutrition_goals_pct": nutrition_goals_pct,
        "nutrition_goals_sub": goals_sub,
        "meal_consistency": meal_consistency,
        "meal_consistency_sub": consistency_sub,
        "diet_balance_pct": diet_balance_pct,
        "period": period,
    }
