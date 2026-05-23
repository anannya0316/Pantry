"""Tests for chatbot/tools/nutrition.py."""
import pytest
from unittest.mock import patch, MagicMock

_MOD = "chatbot.tools.nutrition"


class TestLogRecipe:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.nutrition import log_recipe
        result = log_recipe("", "Pasta", "lunch")
        assert result["success"] is False
        assert "user_id" in result["error"]

    def test_empty_meal_name_fails(self):
        from chatbot.tools.nutrition import log_recipe
        result = log_recipe("u1", "  ", "lunch")
        assert result["success"] is False
        assert "meal_name" in result["error"]

    def test_empty_meal_type_fails(self):
        from chatbot.tools.nutrition import log_recipe
        result = log_recipe("u1", "Pasta", "  ")
        assert result["success"] is False
        assert "meal_type" in result["error"]

    def test_successful_log(self):
        from chatbot.tools.nutrition import log_recipe
        nutrition = {"calories": 500.0, "protein_g": 20.0, "carbs_g": 60.0, "fat_g": 10.0,
                     "fiber_g": 5.0, "vitamin_c_mg": 10.0, "iron_mg": 2.0, "calcium_mg": 50.0}
        with (
            patch(f"{_MOD}.fetch_nutrition", return_value=nutrition),
            patch(f"{_MOD}.get_profile", return_value={"goals": ["Eat healthier"]}),
            patch(f"{_MOD}.get_daily_targets", return_value={"calories": 2200, "protein_g": 90,
                  "carbs_g": 250, "fat_g": 70, "fiber_g": 35, "vitamin_c_mg": 90, "iron_mg": 12, "calcium_mg": 1000}),
            patch(f"{_MOD}.calculate_meal_health_score", return_value=72.5),
            patch(f"{_MOD}.insert_nutrition_log"),
        ):
            result = log_recipe("u1", "Pasta", "lunch")
        assert result["success"] is True
        assert result["health_score"] == 72.5
        assert result["meal_name"] == "Pasta"

    def test_no_profile_uses_empty_goals(self):
        from chatbot.tools.nutrition import log_recipe
        with (
            patch(f"{_MOD}.fetch_nutrition", return_value={}),
            patch(f"{_MOD}.get_profile", return_value=None),
            patch(f"{_MOD}.get_daily_targets", return_value={"calories": 2200, "protein_g": 90,
                  "carbs_g": 250, "fat_g": 70, "fiber_g": 35, "vitamin_c_mg": 90, "iron_mg": 12, "calcium_mg": 1000}),
            patch(f"{_MOD}.calculate_meal_health_score", return_value=50.0),
            patch(f"{_MOD}.insert_nutrition_log"),
        ):
            result = log_recipe("u1", "Rice", "dinner")
        assert result["success"] is True

    def test_exception_returns_failure(self):
        from chatbot.tools.nutrition import log_recipe
        with patch(f"{_MOD}.fetch_nutrition", side_effect=RuntimeError("LLM down")):
            result = log_recipe("u1", "Pasta", "lunch")
        assert result["success"] is False


class TestGetAllNutritionLogs:
    def test_returns_logs_without_id_field(self):
        from chatbot.tools.nutrition import get_all_nutrition_logs
        logs = [{"_id": "abc", "meal": "Pasta"}, {"_id": "def", "meal": "Rice"}]
        with patch(f"{_MOD}.get_nutrition_logs", return_value=logs):
            result = get_all_nutrition_logs("u1")
        assert result["success"] is True
        assert all("_id" not in log for log in result["logs"])
        assert len(result["logs"]) == 2

    def test_exception_returns_failure(self):
        from chatbot.tools.nutrition import get_all_nutrition_logs
        with patch(f"{_MOD}.get_nutrition_logs", side_effect=RuntimeError("DB down")):
            result = get_all_nutrition_logs("u1")
        assert result["success"] is False


class TestGetNutritionLogByMealName:
    def test_empty_name_fails(self):
        from chatbot.tools.nutrition import get_nutrition_log_by_meal_name
        result = get_nutrition_log_by_meal_name("u1", "  ")
        assert result["success"] is False
        assert "meal_name" in result["error"]

    def test_returns_matching_logs(self):
        from chatbot.tools.nutrition import get_nutrition_log_by_meal_name
        logs = [{"_id": "x", "meal": "Pasta", "nutrition": {}}]
        with patch(f"{_MOD}.get_nutrition_log_by_meal", return_value=logs):
            result = get_nutrition_log_by_meal_name("u1", "pasta")
        assert result["success"] is True
        assert len(result["logs"]) == 1
        assert "_id" not in result["logs"][0]

    def test_exception_returns_failure(self):
        from chatbot.tools.nutrition import get_nutrition_log_by_meal_name
        with patch(f"{_MOD}.get_nutrition_log_by_meal", side_effect=RuntimeError("crash")):
            result = get_nutrition_log_by_meal_name("u1", "pasta")
        assert result["success"] is False
