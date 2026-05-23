"""Tests for chatbot/tools/meal_plan.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

_MOD = "chatbot.tools.meal_plan"


class TestGetMealPlanItem:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.meal_plan import get_meal_plan_item
        result = get_meal_plan_item(user_id="")
        assert result["success"] is False

    def test_success_returns_data(self):
        from chatbot.tools.meal_plan import get_meal_plan_item
        with patch(f"{_MOD}.get_meal_plan_service", return_value={"meals": {}}):
            result = get_meal_plan_item(user_id="u1")
        assert result["success"] is True
        assert "data" in result

    def test_http_exception_returns_failure(self):
        from chatbot.tools.meal_plan import get_meal_plan_item
        with patch(f"{_MOD}.get_meal_plan_service", side_effect=HTTPException(404, "not found")):
            result = get_meal_plan_item(user_id="u1")
        assert result["success"] is False

    def test_unexpected_exception_returns_failure(self):
        from chatbot.tools.meal_plan import get_meal_plan_item
        with patch(f"{_MOD}.get_meal_plan_service", side_effect=RuntimeError("crash")):
            result = get_meal_plan_item(user_id="u1")
        assert result["success"] is False


class TestAddMeal:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.meal_plan import add_meal
        result = add_meal("", "Pasta", "Monday", "dinner")
        assert result["success"] is False

    def test_invalid_meal_type_fails(self):
        from chatbot.tools.meal_plan import add_meal
        result = add_meal("u1", "Chips", "Monday", "snack")
        assert result["success"] is False
        assert "breakfast, lunch" in result["error"].lower() or "dinner" in result["error"].lower()

    def test_valid_meal_type_breakfast(self):
        from chatbot.tools.meal_plan import add_meal
        with (
            patch(f"{_MOD}.add_meal_service", return_value={"message": "ok", "ingredients": []}),
            patch(f"{_MOD}.store_nutrition_nested"),
            patch("threading.Thread") as mock_thread,
        ):
            mock_thread.return_value.start = MagicMock()
            result = add_meal("u1", "Oatmeal", "Monday", "breakfast")
        assert result["success"] is True

    def test_http_exception_returns_failure(self):
        from chatbot.tools.meal_plan import add_meal
        with patch(f"{_MOD}.add_meal_service", side_effect=HTTPException(400, "bad")):
            result = add_meal("u1", "Oatmeal", "Monday", "breakfast")
        assert result["success"] is False

    def test_meal_type_case_insensitive(self):
        from chatbot.tools.meal_plan import add_meal
        with (
            patch(f"{_MOD}.add_meal_service", return_value={"message": "ok", "ingredients": []}),
            patch("threading.Thread") as mock_thread,
        ):
            mock_thread.return_value.start = MagicMock()
            result = add_meal("u1", "Eggs", "Tuesday", "BREAKFAST")
        assert result["success"] is True


class TestUpdateMealPlanItem:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.meal_plan import update_meal_plan_item
        result = update_meal_plan_item("", "Pasta")
        assert result["success"] is False

    def test_missing_meal_day_fails(self):
        from chatbot.tools.meal_plan import update_meal_plan_item
        result = update_meal_plan_item("u1", "Pasta", meal_type="lunch")
        assert result["success"] is False
        assert "meal_day" in result["missing_fields"]

    def test_missing_meal_type_fails(self):
        from chatbot.tools.meal_plan import update_meal_plan_item
        result = update_meal_plan_item("u1", "Pasta", meal_day="Monday")
        assert result["success"] is False
        assert "meal_type" in result["missing_fields"]

    def test_invalid_meal_type_fails(self):
        from chatbot.tools.meal_plan import update_meal_plan_item
        result = update_meal_plan_item("u1", "Pasta", meal_day="Monday", meal_type="brunch")
        assert result["success"] is False

    def test_success(self):
        from chatbot.tools.meal_plan import update_meal_plan_item
        with (
            patch(f"{_MOD}.add_meal_service", return_value={"message": "ok", "ingredients": []}),
            patch(f"{_MOD}.store_nutrition_nested"),
            patch("threading.Thread") as mock_thread,
        ):
            mock_thread.return_value.start = MagicMock()
            result = update_meal_plan_item("u1", "Pasta", meal_day="Monday", meal_type="dinner")
        assert result["success"] is True


class TestDeleteMealTool:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.meal_plan import delete_meal_tool
        result = delete_meal_tool("", "Monday", "dinner")
        assert result["success"] is False

    def test_success(self):
        from chatbot.tools.meal_plan import delete_meal_tool
        with patch(f"{_MOD}.delete_meal_service", return_value={"message": "deleted"}):
            result = delete_meal_tool("u1", "Monday", "dinner")
        assert result["success"] is True

    def test_http_exception_returns_failure(self):
        from chatbot.tools.meal_plan import delete_meal_tool
        with patch(f"{_MOD}.delete_meal_service", side_effect=HTTPException(404, "not found")):
            result = delete_meal_tool("u1", "Monday", "dinner")
        assert result["success"] is False
