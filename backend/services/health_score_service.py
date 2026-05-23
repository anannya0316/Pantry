from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_IST = ZoneInfo("Asia/Kolkata")

# ── keyword sets ──────────────────────────────────────────────────────────────

_VEGETABLE_KEYWORDS = frozenset({
    "salad", "spinach", "broccoli", "carrot", "kale", "lettuce", "tomato",
    "cucumber", "pepper", "zucchini", "peas", "lentil", "lentils", "dal",
    "sabzi", "bhaji", "palak", "methi", "gourd", "cauliflower", "cabbage",
    "mushroom", "asparagus", "celery", "beet", "squash", "pumpkin",
    "arugula", "greens", "capsicum", "eggplant", "artichoke", "leek",
    "radish", "turnip", "okra", "bok choy", "vegetable", "veggie", "veggies",
    "coleslaw", "stir fry", "stir-fry", "saag", "rasam", "sambar",
})

_FRUIT_KEYWORDS = frozenset({
    "apple", "banana", "orange", "mango", "berry", "strawberry", "blueberry",
    "raspberry", "grape", "watermelon", "melon", "peach", "pear", "plum",
    "cherry", "kiwi", "pineapple", "papaya", "guava", "pomegranate",
    "citrus", "apricot", "lychee", "fruit",
})

_PROCESSED_KEYWORDS = frozenset({
    "chips", "fries", "burger", "soda", "cola", "pepsi", "sprite", "fanta",
    "candy", "cake", "cookie", "donut", "nuggets", "hot dog",
    "instant noodle", "instant ramen", "cup noodle", "junk",
    "frozen dinner", "microwave meal", "processed",
})

_HEALTHY_PROTEIN_KEYWORDS = frozenset({
    "chicken", "turkey", "fish", "salmon", "tuna", "sardine", "mackerel",
    "shrimp", "prawn", "egg", "eggs", "tofu", "tempeh", "lentil", "lentils",
    "chickpea", "chickpeas", "bean", "beans", "legume", "legumes",
    "cottage cheese", "greek yogurt", "paneer", "dal", "edamame", "quinoa",
})

_WHOLE_GRAIN_KEYWORDS = frozenset({
    "brown rice", "oats", "oatmeal", "whole wheat", "barley",
    "millet", "bulgur", "rye", "whole grain", "multigrain", "bran",
    "wholewheat", "whole-wheat", "quinoa",
})

_FAST_FOOD_KEYWORDS = frozenset({
    "mcdonald", "kfc", "burger king", "subway", "domino", "dominos",
    "pizza hut", "wendy", "taco bell", "delivery", "takeout",
    "take-out", "takeaway", "chipotle", "popeyes",
})

_SUGARY_DRINK_KEYWORDS = frozenset({
    "soda", "cola", "pepsi", "coke", "sprite", "fanta",
    "energy drink", "red bull", "monster", "mountain dew",
})

_FRIED_KEYWORDS = frozenset({
    "fried", "deep fried", "deep-fried", "battered", "fritter", "tempura",
})

_CONVENIENCE_KEYWORDS = frozenset({
    "instant noodle", "instant ramen", "cup noodle", "frozen",
    "packaged", "mcdonald", "kfc", "domino", "delivery",
    "takeout", "takeaway", "microwave",
})

# ── helpers ───────────────────────────────────────────────────────────────────


def _kw_match(name_lower: str, keywords: frozenset) -> int:
    return sum(1 for kw in keywords if kw in name_lower)


def _to_ist_hour(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(_IST).hour


# ── component A: macro balance (25%) ─────────────────────────────────────────


def _macro_balance_score(nutrition: dict, daily_targets: dict) -> float:
    """Score each macro against per-meal target (daily / 3). Small deviations
    are tolerated; deviation_pct is mapped linearly to 0-100."""

    def _component(actual: float, daily_target: float) -> float:
        if daily_target <= 0:
            return 100.0
        per_meal = daily_target / 3.0
        deviation_pct = abs(actual - per_meal) / per_meal * 100.0
        return max(0.0, 100.0 - deviation_pct)

    protein = _component(
        nutrition.get("protein_g", 0.0),
        daily_targets.get("protein_g", 90.0),
    )
    fiber = _component(
        nutrition.get("fiber_g", 0.0),
        daily_targets.get("fiber_g", 35.0),
    )
    fat = _component(
        nutrition.get("fat_g", 0.0),
        daily_targets.get("fat_g", 70.0),
    )
    calories = _component(
        nutrition.get("calories", 0.0),
        daily_targets.get("calories", 2200.0),
    )
    return (protein + fiber + fat + calories) / 4.0


# ── component B: food quality (25%) ──────────────────────────────────────────


def _food_quality_score(meal_name: str, nutrition: dict) -> float:
    """Keyword-based food quality scoring, augmented by nutrition signals when
    the meal name is too generic to match keywords."""

    n = meal_name.lower()

    veg_matches = _kw_match(n, _VEGETABLE_KEYWORDS)
    fruit_matches = _kw_match(n, _FRUIT_KEYWORDS)
    proc_matches = _kw_match(n, _PROCESSED_KEYWORDS)
    prot_matches = _kw_match(n, _HEALTHY_PROTEIN_KEYWORDS)
    grain_matches = _kw_match(n, _WHOLE_GRAIN_KEYWORDS)

    vegetable_score = min(100.0, veg_matches * 60.0)
    fruit_score = min(100.0, fruit_matches * 60.0)
    processed_penalty = max(0.0, 100.0 - proc_matches * 60.0)
    protein_quality = min(100.0, prot_matches * 60.0)
    whole_food_score = min(100.0, grain_matches * 60.0)

    # Boost scores from nutrition data when name alone is uninformative
    fiber_g = nutrition.get("fiber_g", 0.0)
    vitamin_c_mg = nutrition.get("vitamin_c_mg", 0.0)
    protein_g = nutrition.get("protein_g", 0.0)

    if fiber_g >= 5.0:
        vegetable_score = max(vegetable_score, 50.0)
        whole_food_score = max(whole_food_score, 40.0)
    if vitamin_c_mg >= 15.0:
        vegetable_score = max(vegetable_score, 60.0)
        fruit_score = max(fruit_score, 30.0)
    if protein_g >= 20.0:
        protein_quality = max(protein_quality, 50.0)

    return (
        vegetable_score * 0.30
        + fruit_score * 0.15
        + processed_penalty * 0.30
        + protein_quality * 0.15
        + whole_food_score * 0.10
    )


# ── component C: micronutrient coverage (15%) ─────────────────────────────────


def _micronutrient_score(nutrition: dict, daily_targets: dict) -> float:
    """Diversity (how many micros are non-zero) + coverage (how close each is
    to its per-meal share of the daily target)."""

    micro_keys = ("vitamin_c_mg", "iron_mg", "calcium_mg", "fiber_g")
    non_zero = 0
    coverages = []

    for key in micro_keys:
        daily_target = daily_targets.get(key, 1.0)
        per_meal_target = max(daily_target / 3.0, 1e-9)
        actual = nutrition.get(key, 0.0)

        if actual > 0:
            non_zero += 1

        coverages.append(min(actual / per_meal_target, 1.0))

    diversity_score = (non_zero / len(micro_keys)) * 100.0
    coverage_score = (sum(coverages) / len(coverages)) * 100.0

    return diversity_score * 0.5 + coverage_score * 0.5


# ── component D: meal consistency (15%) ───────────────────────────────────────


def _meal_consistency_score(
    meal_type: str,
    created_at: datetime,
    nutrition: dict,
) -> float:
    """Scores timing alignment and calorie reasonableness for the meal type."""

    hour = _to_ist_hour(created_at)

    _windows = {
        "breakfast": (5, 10),
        "lunch": (11, 15),
        "dinner": (17, 21),
    }

    window = _windows.get(meal_type)
    if window:
        if window[0] <= hour <= window[1]:
            meal_regularity = 100.0
        else:
            dist = max(window[0] - hour, hour - window[1])
            meal_regularity = max(0.0, 100.0 - dist * 15.0)
    else:
        meal_regularity = 70.0

    if hour >= 22:
        meal_regularity = min(meal_regularity, 30.0)

    calories = nutrition.get("calories", 0.0)
    _cal_ranges = {
        "breakfast": (250.0, 600.0),
        "lunch": (350.0, 750.0),
        "dinner": (350.0, 800.0),
    }
    low, high = _cal_ranges.get(meal_type, (200.0, 800.0))

    if calories == 0.0:
        calorie_stability = 50.0
    elif low <= calories <= high:
        calorie_stability = 100.0
    elif calories < low:
        calorie_stability = max(0.0, calories / low * 100.0)
    else:
        calorie_stability = max(0.0, high / calories * 100.0)

    meal_completion = 100.0  # logging the meal itself counts

    return (
        meal_regularity * 0.40
        + calorie_stability * 0.30
        + meal_completion * 0.30
    )


# ── component E: lifestyle signals (10%) ──────────────────────────────────────


def _lifestyle_score(
    meal_name: str,
    created_at: datetime,
) -> float:
    """Penalises late-night eating, fast-food, sugary drinks, and fried food."""

    hour = _to_ist_hour(created_at)

    if hour >= 23 or hour <= 4:
        late_eating_score = 0.0
    elif hour >= 21:
        late_eating_score = 40.0
    else:
        late_eating_score = 100.0

    n = meal_name.lower()

    eating_out_score = 30.0 if _kw_match(n, _FAST_FOOD_KEYWORDS) > 0 else 100.0
    sugary_drink_score = 0.0 if _kw_match(n, _SUGARY_DRINK_KEYWORDS) > 0 else 100.0
    fried_score = 30.0 if _kw_match(n, _FRIED_KEYWORDS) > 0 else 100.0

    return (
        late_eating_score * 0.35
        + eating_out_score * 0.25
        + sugary_drink_score * 0.20
        + fried_score * 0.20
    )


# ── component F: sustainability (10%) ─────────────────────────────────────────


def _sustainability_score(meal_name: str, nutrition: dict) -> float:
    """Flags extreme restriction, bingeing, convenience-food dependence, and
    macro imbalance."""

    calories = nutrition.get("calories", 0.0)

    if 0.0 < calories < 100.0:
        restriction_score = 20.0
    elif calories == 0.0:
        restriction_score = 50.0  # no data → neutral
    else:
        restriction_score = 100.0

    if calories > 1200.0:
        binge_score = max(0.0, 100.0 - (calories - 1200.0) / 12.0)
    else:
        binge_score = 100.0

    n = meal_name.lower()
    variety_score = 30.0 if _kw_match(n, _CONVENIENCE_KEYWORDS) > 0 else 100.0

    has_protein = nutrition.get("protein_g", 0.0) >= 5.0
    has_carbs = nutrition.get("carbs_g", 0.0) >= 10.0
    has_fat = nutrition.get("fat_g", 0.0) >= 3.0
    balance_score = sum([has_protein, has_carbs, has_fat]) / 3.0 * 100.0

    return (
        restriction_score * 0.30
        + binge_score * 0.30
        + variety_score * 0.25
        + balance_score * 0.15
    )


# ── public API ────────────────────────────────────────────────────────────────


def calculate_meal_health_score(
    meal_name: str,
    nutrition: dict,
    meal_type: str,
    created_at: datetime,
    daily_targets: dict,
) -> float:
    """Return a 0-100 health score for a single logged meal.

    Weights:
        macro_balance      25%
        food_quality       25%
        micronutrient      15%
        meal_consistency   15%
        lifestyle          10%
        sustainability     10%
    """
    macro = _macro_balance_score(nutrition, daily_targets)
    quality = _food_quality_score(meal_name, nutrition)
    micro = _micronutrient_score(nutrition, daily_targets)
    consistency = _meal_consistency_score(meal_type, created_at, nutrition)
    lifestyle = _lifestyle_score(meal_name, created_at)
    sustainability = _sustainability_score(meal_name, nutrition)

    score = (
        macro * 0.25
        + quality * 0.25
        + micro * 0.15
        + consistency * 0.15
        + lifestyle * 0.10
        + sustainability * 0.10
    )

    return round(min(100.0, max(0.0, score)), 1)
