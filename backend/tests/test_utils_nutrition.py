"""Tests for utils/nutrition_utils.py."""
import pytest
from utils.nutrition_utils import sum_nutrition, get_active_meals, get_all_consumed_meals
from constants.nutrition_constants import MACRO_KEYS


def _meal(nutrition=None, valid=True, skipped=False, consumed=False, **kwargs):
    m = {"valid": valid, "skipped": skipped, "consumed": consumed}
    if nutrition is not None:
        m["nutrition"] = nutrition
    m.update(kwargs)
    return m


def _meal_doc(days: dict) -> dict:
    return {"meals": days}


# ---------------------------------------------------------------------------
# sum_nutrition
# ---------------------------------------------------------------------------

class TestSumNutrition:
    def test_empty_list_returns_all_zeros(self):
        result = sum_nutrition([])
        assert all(result[k] == 0.0 for k in MACRO_KEYS)

    def test_single_meal_matches_its_nutrition(self):
        nut = {"calories": 500.0, "protein_g": 30.0, "carbs_g": 60.0, "fat_g": 15.0,
               "fiber_g": 5.0, "vitamin_c_mg": 10.0, "iron_mg": 2.0, "calcium_mg": 100.0}
        result = sum_nutrition([{"nutrition": nut}])
        for k in MACRO_KEYS:
            assert result[k] == pytest.approx(nut[k])

    def test_two_meals_sums_correctly(self):
        nut = {"calories": 300.0, "protein_g": 20.0, "carbs_g": 40.0, "fat_g": 10.0,
               "fiber_g": 4.0, "vitamin_c_mg": 8.0, "iron_mg": 1.5, "calcium_mg": 80.0}
        result = sum_nutrition([{"nutrition": nut}, {"nutrition": nut}])
        for k in MACRO_KEYS:
            assert result[k] == pytest.approx(nut[k] * 2)

    def test_meal_with_no_nutrition_key_treated_as_zeros(self):
        result = sum_nutrition([{"name": "mystery meal"}])
        assert all(result[k] == 0.0 for k in MACRO_KEYS)

    def test_meal_with_none_nutrition_treated_as_zeros(self):
        result = sum_nutrition([{"nutrition": None}])
        assert all(result[k] == 0.0 for k in MACRO_KEYS)

    def test_partial_nutrition_keys(self):
        result = sum_nutrition([{"nutrition": {"calories": 200.0}}])
        assert result["calories"] == pytest.approx(200.0)
        assert result["protein_g"] == pytest.approx(0.0)

    def test_returns_all_macro_keys(self):
        result = sum_nutrition([])
        assert set(result.keys()) == set(MACRO_KEYS)


# ---------------------------------------------------------------------------
# get_active_meals
# ---------------------------------------------------------------------------

class TestGetActiveMeals:
    def test_empty_meal_doc_returns_empty(self):
        assert get_active_meals({"meals": {}}) == []

    def test_returns_latest_valid_non_skipped_meal_per_slot(self):
        doc = _meal_doc({
            "Monday": {
                "breakfast": [
                    _meal({"calories": 300.0}, valid=True, skipped=False),
                    _meal({"calories": 350.0}, valid=True, skipped=False),
                ]
            }
        })
        result = get_active_meals(doc)
        # reversed order — last in list is "latest"; should pick the last valid
        assert len(result) == 1
        assert result[0]["nutrition"]["calories"] == 350.0

    def test_skipped_meals_are_excluded(self):
        doc = _meal_doc({
            "Monday": {
                "lunch": [
                    _meal({"calories": 500.0}, valid=True, skipped=True),
                ]
            }
        })
        result = get_active_meals(doc)
        assert result == []

    def test_invalid_meals_are_excluded(self):
        doc = _meal_doc({
            "Monday": {
                "dinner": [
                    _meal({"calories": 600.0}, valid=False, skipped=False),
                ]
            }
        })
        result = get_active_meals(doc)
        assert result == []

    def test_active_meal_has_day_and_meal_type_injected(self):
        doc = _meal_doc({
            "Tuesday": {
                "lunch": [_meal({"calories": 450.0}, valid=True)]
            }
        })
        result = get_active_meals(doc)
        assert result[0]["day"] == "Tuesday"
        assert result[0]["meal_type"] == "lunch"

    def test_multiple_days_and_slots(self):
        doc = _meal_doc({
            "Monday": {
                "breakfast": [_meal({"calories": 300.0}, valid=True)],
                "lunch": [_meal({"calories": 500.0}, valid=True)],
            },
            "Tuesday": {
                "dinner": [_meal({"calories": 600.0}, valid=True)],
            },
        })
        result = get_active_meals(doc)
        assert len(result) == 3

    def test_only_first_valid_from_reversed_slot(self):
        # get_active_meals iterates reversed and breaks at first valid=True
        doc = _meal_doc({
            "Monday": {
                "breakfast": [
                    _meal({"calories": 100.0}, valid=False),
                    _meal({"calories": 200.0}, valid=True),
                    _meal({"calories": 300.0}, valid=True),
                ]
            }
        })
        result = get_active_meals(doc)
        assert len(result) == 1
        assert result[0]["nutrition"]["calories"] == 300.0


# ---------------------------------------------------------------------------
# get_all_consumed_meals
# ---------------------------------------------------------------------------

class TestGetAllConsumedMeals:
    def test_empty_meal_doc_returns_empty(self):
        assert get_all_consumed_meals({"meals": {}}) == []

    def test_returns_only_consumed_true_meals(self):
        doc = _meal_doc({
            "Monday": {
                "breakfast": [
                    _meal({"calories": 300.0}, consumed=True),
                    _meal({"calories": 200.0}, consumed=False),
                ]
            }
        })
        result = get_all_consumed_meals(doc)
        assert len(result) == 1
        assert result[0]["nutrition"]["calories"] == 300.0

    def test_consumed_meal_has_day_and_meal_type(self):
        doc = _meal_doc({
            "Wednesday": {
                "dinner": [_meal({}, consumed=True)]
            }
        })
        result = get_all_consumed_meals(doc)
        assert result[0]["day"] == "Wednesday"
        assert result[0]["meal_type"] == "dinner"

    def test_no_consumed_meals_returns_empty(self):
        doc = _meal_doc({
            "Monday": {
                "lunch": [_meal({}, consumed=False), _meal({}, consumed=False)]
            }
        })
        assert get_all_consumed_meals(doc) == []

    def test_multiple_consumed_meals_across_days(self):
        doc = _meal_doc({
            "Monday": {
                "breakfast": [_meal({}, consumed=True)],
                "lunch": [_meal({}, consumed=True), _meal({}, consumed=False)],
            },
            "Tuesday": {
                "dinner": [_meal({}, consumed=True)],
            },
        })
        result = get_all_consumed_meals(doc)
        assert len(result) == 3

    def test_consumed_not_set_treated_as_false(self):
        doc = _meal_doc({
            "Monday": {
                "breakfast": [{"nutrition": {}}]  # no "consumed" key
            }
        })
        assert get_all_consumed_meals(doc) == []
