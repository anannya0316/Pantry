"""Tests for services/health_score_service.py.

All functions under test are pure (no DB / LLM calls), so no mocking is needed.
"""
import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from services.health_score_service import (
    _macro_balance_score,
    _food_quality_score,
    _micronutrient_score,
    _meal_consistency_score,
    _lifestyle_score,
    _sustainability_score,
    calculate_meal_health_score,
)

_IST = ZoneInfo("Asia/Kolkata")

_DEFAULT_TARGETS = {
    "calories": 2200.0,
    "protein_g": 90.0,
    "carbs_g": 250.0,
    "fat_g": 70.0,
    "fiber_g": 35.0,
    "vitamin_c_mg": 90.0,
    "iron_mg": 12.0,
    "calcium_mg": 1000.0,
}


def _ist(hour: int, minute: int = 0) -> datetime:
    """Return a fixed IST datetime for a given hour."""
    return datetime(2024, 1, 15, hour, minute, tzinfo=_IST)


# ---------------------------------------------------------------------------
# _macro_balance_score
# ---------------------------------------------------------------------------

class TestMacroBalanceScore:
    def test_perfect_macros_scores_100(self):
        perfect = {
            "protein_g": 30.0,   # 90/3
            "fiber_g": 35.0 / 3,
            "fat_g": 70.0 / 3,
            "calories": 2200.0 / 3,
        }
        score = _macro_balance_score(perfect, _DEFAULT_TARGETS)
        assert score == pytest.approx(100.0, abs=1e-6)

    def test_zero_nutrition_scores_low(self):
        score = _macro_balance_score({}, _DEFAULT_TARGETS)
        assert score < 50.0

    def test_large_deviation_cannot_go_below_zero(self):
        extreme = {"protein_g": 1000.0, "fiber_g": 0.0, "fat_g": 0.0, "calories": 0.0}
        score = _macro_balance_score(extreme, _DEFAULT_TARGETS)
        assert score >= 0.0

    def test_zero_target_skips_that_macro(self):
        targets = {**_DEFAULT_TARGETS, "protein_g": 0.0}
        nutrition = {"protein_g": 50.0, "fiber_g": 35.0 / 3, "fat_g": 70.0 / 3, "calories": 2200.0 / 3}
        score = _macro_balance_score(nutrition, targets)
        assert score >= 0.0


# ---------------------------------------------------------------------------
# _food_quality_score
# ---------------------------------------------------------------------------

class TestFoodQualityScore:
    def test_vegetable_heavy_meal_scores_high(self):
        score = _food_quality_score("spinach salad with broccoli", {})
        assert score > 50.0

    def test_processed_junk_scores_low(self):
        score = _food_quality_score("chips and soda", {})
        assert score < 50.0

    def test_healthy_protein_boosts_score(self):
        score = _food_quality_score("grilled salmon with salad", {})
        assert score > 50.0

    def test_whole_grain_boosts_score(self):
        score = _food_quality_score("brown rice with vegetables", {})
        assert score > 50.0

    def test_high_fiber_nutrition_boosts_generic_name(self):
        score_no_fiber = _food_quality_score("mixed dish", {})
        score_high_fiber = _food_quality_score("mixed dish", {"fiber_g": 8.0})
        assert score_high_fiber >= score_no_fiber

    def test_high_vitamin_c_boosts_vegetable_score(self):
        score_no_vit = _food_quality_score("plain dish", {})
        score_vit = _food_quality_score("plain dish", {"vitamin_c_mg": 20.0})
        assert score_vit >= score_no_vit

    def test_high_protein_nutrition_boosts_protein_quality(self):
        score_low = _food_quality_score("plain dish", {"protein_g": 5.0})
        score_high = _food_quality_score("plain dish", {"protein_g": 25.0})
        assert score_high >= score_low

    def test_score_bounded_0_to_100(self):
        for name in ("pizza", "salad", "chips", "quinoa oats", "McDonalds"):
            score = _food_quality_score(name, {})
            assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# _micronutrient_score
# ---------------------------------------------------------------------------

class TestMicronutrientScore:
    def test_all_zeros_scores_zero(self):
        score = _micronutrient_score({}, _DEFAULT_TARGETS)
        assert score == pytest.approx(0.0)

    def test_full_coverage_scores_100(self):
        full = {
            "vitamin_c_mg": 90.0,   # daily target
            "iron_mg": 12.0,
            "calcium_mg": 1000.0,
            "fiber_g": 35.0,
        }
        score = _micronutrient_score(full, _DEFAULT_TARGETS)
        assert score == pytest.approx(100.0)

    def test_partial_coverage_between_0_and_100(self):
        partial = {"vitamin_c_mg": 30.0, "iron_mg": 0.0, "calcium_mg": 0.0, "fiber_g": 0.0}
        score = _micronutrient_score(partial, _DEFAULT_TARGETS)
        assert 0.0 < score < 100.0

    def test_score_bounded_0_to_100(self):
        over = {"vitamin_c_mg": 9000.0, "iron_mg": 9000.0, "calcium_mg": 9000.0, "fiber_g": 9000.0}
        score = _micronutrient_score(over, _DEFAULT_TARGETS)
        assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# _meal_consistency_score
# ---------------------------------------------------------------------------

class TestMealConsistencyScore:
    def test_breakfast_at_7am_scores_high(self):
        score = _meal_consistency_score("breakfast", _ist(7), {"calories": 400.0})
        assert score >= 80.0

    def test_breakfast_at_11pm_scores_low(self):
        score = _meal_consistency_score("breakfast", _ist(23), {"calories": 400.0})
        assert score < 70.0

    def test_lunch_at_1pm_scores_high(self):
        score = _meal_consistency_score("lunch", _ist(13), {"calories": 500.0})
        assert score >= 80.0

    def test_dinner_at_8pm_scores_high(self):
        score = _meal_consistency_score("dinner", _ist(20), {"calories": 600.0})
        assert score >= 80.0

    def test_late_night_caps_regularity(self):
        score = _meal_consistency_score("dinner", _ist(23), {"calories": 600.0})
        # hour >= 22 caps meal_regularity at 30; still lower than well-timed dinner
        assert score < 80.0

    def test_zero_calories_is_neutral_not_penalised(self):
        score_zero = _meal_consistency_score("lunch", _ist(12), {"calories": 0.0})
        score_ok = _meal_consistency_score("lunch", _ist(12), {"calories": 500.0})
        assert score_zero > 0.0
        assert score_ok > score_zero

    def test_too_few_calories_reduces_stability(self):
        score_low = _meal_consistency_score("breakfast", _ist(8), {"calories": 100.0})
        score_ok = _meal_consistency_score("breakfast", _ist(8), {"calories": 400.0})
        assert score_ok > score_low

    def test_too_many_calories_reduces_stability(self):
        score_excess = _meal_consistency_score("dinner", _ist(19), {"calories": 2000.0})
        score_ok = _meal_consistency_score("dinner", _ist(19), {"calories": 600.0})
        assert score_ok > score_excess

    def test_unknown_meal_type_returns_neutral(self):
        score = _meal_consistency_score("snack", _ist(10), {"calories": 200.0})
        assert score > 0.0


# ---------------------------------------------------------------------------
# _lifestyle_score
# ---------------------------------------------------------------------------

class TestLifestyleScore:
    def test_daytime_healthy_meal_scores_100(self):
        score = _lifestyle_score("grilled chicken", _ist(12))
        assert score == pytest.approx(100.0)

    def test_late_night_after_23_scores_zero_late_eating(self):
        score = _lifestyle_score("chicken salad", _ist(23))
        assert score < 80.0

    def test_very_late_night_0_to_4_scores_zero_late_eating(self):
        score = _lifestyle_score("rice", _ist(2))
        assert score < 70.0

    def test_fast_food_penalised(self):
        score_clean = _lifestyle_score("grilled chicken", _ist(12))
        score_ff = _lifestyle_score("McDonalds burger", _ist(12))
        assert score_clean > score_ff

    def test_sugary_drink_penalised(self):
        score_clean = _lifestyle_score("water with meal", _ist(12))
        score_soda = _lifestyle_score("pepsi cola", _ist(12))
        assert score_clean > score_soda

    def test_fried_food_penalised(self):
        score_clean = _lifestyle_score("baked chicken", _ist(12))
        score_fried = _lifestyle_score("deep fried chicken", _ist(12))
        assert score_clean > score_fried

    def test_score_bounded_0_to_100(self):
        for name in ("kfc", "soda", "deep fried nuggets", "salad", "oatmeal"):
            score = _lifestyle_score(name, _ist(12))
            assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# _sustainability_score
# ---------------------------------------------------------------------------

class TestSustainabilityScore:
    def test_balanced_meal_scores_high(self):
        nutrition = {"calories": 500.0, "protein_g": 30.0, "carbs_g": 60.0, "fat_g": 15.0}
        score = _sustainability_score("dal rice", nutrition)
        assert score > 70.0

    def test_extreme_restriction_penalised(self):
        score_restricted = _sustainability_score("small salad", {"calories": 50.0})
        score_normal = _sustainability_score("balanced meal", {"calories": 500.0})
        assert score_normal > score_restricted

    def test_binge_over_1200_penalised(self):
        score_ok = _sustainability_score("large meal", {"calories": 800.0, "protein_g": 40.0, "carbs_g": 100.0, "fat_g": 20.0})
        score_binge = _sustainability_score("huge binge", {"calories": 2000.0, "protein_g": 40.0, "carbs_g": 100.0, "fat_g": 20.0})
        assert score_ok > score_binge

    def test_convenience_food_penalised(self):
        score_clean = _sustainability_score("home cooked rice", {"calories": 500.0, "protein_g": 20.0, "carbs_g": 80.0, "fat_g": 10.0})
        score_instant = _sustainability_score("instant noodles", {"calories": 500.0, "protein_g": 20.0, "carbs_g": 80.0, "fat_g": 10.0})
        assert score_clean > score_instant

    def test_missing_macros_reduces_balance(self):
        no_macros = _sustainability_score("mystery food", {})
        with_macros = _sustainability_score("balanced food", {"protein_g": 20.0, "carbs_g": 50.0, "fat_g": 10.0, "calories": 400.0})
        assert with_macros > no_macros

    def test_score_bounded_0_to_100(self):
        for name, nut in [
            ("chips", {"calories": 3000.0}),
            ("broccoli", {"calories": 30.0}),
            ("instant ramen", {"calories": 500.0, "protein_g": 10.0, "carbs_g": 60.0, "fat_g": 15.0}),
        ]:
            score = _sustainability_score(name, nut)
            assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# calculate_meal_health_score (integration)
# ---------------------------------------------------------------------------

class TestCalculateMealHealthScore:
    def _good_nutrition(self):
        return {
            "calories": 500.0,
            "protein_g": 30.0,
            "carbs_g": 60.0,
            "fat_g": 15.0,
            "fiber_g": 8.0,
            "vitamin_c_mg": 30.0,
            "iron_mg": 4.0,
            "calcium_mg": 300.0,
        }

    def test_healthy_lunch_scores_reasonably_high(self):
        score = calculate_meal_health_score(
            meal_name="grilled chicken salad",
            nutrition=self._good_nutrition(),
            meal_type="lunch",
            created_at=_ist(13),
            daily_targets=_DEFAULT_TARGETS,
        )
        assert score >= 50.0

    def test_junk_late_night_scores_low(self):
        score = calculate_meal_health_score(
            meal_name="McDonalds chips and soda",
            nutrition={"calories": 800.0, "protein_g": 5.0, "carbs_g": 100.0, "fat_g": 40.0},
            meal_type="dinner",
            created_at=_ist(23),
            daily_targets=_DEFAULT_TARGETS,
        )
        assert score < 60.0

    def test_score_always_in_0_to_100(self):
        for meal, cal in [("broccoli salad", 50.0), ("instant ramen", 400.0), ("birthday cake", 1800.0)]:
            score = calculate_meal_health_score(
                meal_name=meal,
                nutrition={"calories": cal},
                meal_type="lunch",
                created_at=_ist(12),
                daily_targets=_DEFAULT_TARGETS,
            )
            assert 0.0 <= score <= 100.0

    def test_result_is_rounded_to_one_decimal(self):
        score = calculate_meal_health_score(
            meal_name="oatmeal",
            nutrition=self._good_nutrition(),
            meal_type="breakfast",
            created_at=_ist(8),
            daily_targets=_DEFAULT_TARGETS,
        )
        assert score == round(score, 1)
