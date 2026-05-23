"""Tests for services/nutrition_target_service.py."""
import pytest
from services.nutrition_target_service import get_daily_targets
from constants.nutrition_constants import GOAL_TARGETS


class TestGetDailyTargets:
    def test_empty_goals_returns_eat_healthier(self):
        result = get_daily_targets([])
        assert result == GOAL_TARGETS["eat_healthier"]

    def test_none_goals_returns_eat_healthier(self):
        result = get_daily_targets(None)
        assert result == GOAL_TARGETS["eat_healthier"]

    def test_gain_muscle_goal(self):
        result = get_daily_targets(["Gain muscle"])
        assert result == GOAL_TARGETS["gain_muscle"]

    def test_gain_muscle_case_insensitive(self):
        result = get_daily_targets(["GAIN MUSCLE"])
        assert result == GOAL_TARGETS["gain_muscle"]

    def test_lose_weight_goal(self):
        result = get_daily_targets(["Lose weight"])
        assert result == GOAL_TARGETS["lose_weight"]

    def test_lose_weight_case_insensitive(self):
        result = get_daily_targets(["LOSE WEIGHT"])
        assert result == GOAL_TARGETS["lose_weight"]

    def test_both_conflicting_goals_return_eat_healthier(self):
        result = get_daily_targets(["Gain muscle", "Lose weight"])
        assert result == GOAL_TARGETS["eat_healthier"]

    def test_unrelated_goal_returns_eat_healthier(self):
        result = get_daily_targets(["Eat healthier"])
        assert result == GOAL_TARGETS["eat_healthier"]

    def test_gain_muscle_has_higher_calories_than_lose_weight(self):
        gain = get_daily_targets(["Gain muscle"])
        lose = get_daily_targets(["Lose weight"])
        assert gain["calories"] > lose["calories"]

    def test_gain_muscle_has_higher_protein_than_eat_healthier(self):
        gain = get_daily_targets(["Gain muscle"])
        healthy = get_daily_targets([])
        assert gain["protein_g"] > healthy["protein_g"]

    def test_lose_weight_has_lower_calories_than_eat_healthier(self):
        lose = get_daily_targets(["Lose weight"])
        healthy = get_daily_targets([])
        assert lose["calories"] < healthy["calories"]

    def test_goal_with_extra_whitespace_handled(self):
        result = get_daily_targets(["  gain muscle  "])
        assert result == GOAL_TARGETS["gain_muscle"]

    def test_returned_dict_has_all_required_keys(self):
        required_keys = {"calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "vitamin_c_mg", "iron_mg", "calcium_mg"}
        for goals in [[], ["Gain muscle"], ["Lose weight"]]:
            result = get_daily_targets(goals)
            assert required_keys.issubset(result.keys())
