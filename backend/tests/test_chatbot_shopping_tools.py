"""Tests for chatbot/tools/shopping.py — _is_low and get_shopping_list."""
import pytest
from unittest.mock import patch

_MOD = "chatbot.tools.shopping"


# ---------------------------------------------------------------------------
# _is_low
# ---------------------------------------------------------------------------

class TestIsLow:
    def test_zero_quantity_is_not_low(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(0, "kg") is False

    def test_quantity_above_threshold_is_not_low(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(1.0, "kg") is False  # threshold = 0.5

    def test_quantity_below_threshold_is_low(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(0.3, "kg") is True

    def test_pieces_threshold(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(1, "pieces") is True   # threshold = 2
        assert _is_low(3, "pieces") is False

    def test_ml_threshold(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(100, "ml") is True    # threshold = 250
        assert _is_low(300, "ml") is False

    def test_liter_threshold(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(0.2, "liter") is True   # threshold = 0.5
        assert _is_low(0.6, "liter") is False

    def test_unknown_unit_defaults_to_threshold_1(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(0.5, "mystery_unit") is True
        assert _is_low(1.5, "mystery_unit") is False

    def test_case_insensitive_unit(self):
        from chatbot.tools.shopping import _is_low
        assert _is_low(0.3, "KG") is True


# ---------------------------------------------------------------------------
# get_shopping_list
# ---------------------------------------------------------------------------

class TestGetShoppingList:
    def _inventory(self, items):
        return {"items": items}

    def test_empty_inventory_no_plan_returns_stocked_message(self):
        from chatbot.tools.shopping import get_shopping_list
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": []}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["success"] is True
        assert result["summary"]["total"] == 0
        assert "stocked" in result["message"].lower()

    def test_out_of_stock_item_detected(self):
        from chatbot.tools.shopping import get_shopping_list
        items = [{"display_name": "Milk", "quantity": 0, "unit": "liter", "status": "fresh"}]
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["out_of_stock"] == 1
        assert any(i["name"] == "Milk" for i in result["shopping_list"])

    def test_consumed_item_treated_as_out_of_stock(self):
        from chatbot.tools.shopping import get_shopping_list
        items = [{"display_name": "Rice", "quantity": 1, "unit": "kg", "status": "consumed"}]
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["out_of_stock"] == 1

    def test_expired_item_detected(self):
        from chatbot.tools.shopping import get_shopping_list
        items = [{"display_name": "Yogurt", "quantity": 1, "unit": "kg", "status": "expired"}]
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["expired"] == 1

    def test_low_stock_item_detected(self):
        from chatbot.tools.shopping import get_shopping_list
        items = [{"display_name": "Oil", "quantity": 0.2, "unit": "liter", "status": "fresh"}]
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["low_stock"] == 1

    def test_meal_plan_ingredient_not_in_inventory_added(self):
        from chatbot.tools.shopping import get_shopping_list
        items = []
        plan = {
            "success": True,
            "data": {
                "meals": {
                    "Monday": {
                        "dinner": [{"meal_name": "Pasta", "ingredients": ["Pasta", "Tomato Sauce"]}]
                    }
                }
            }
        }
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value=plan),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["needed_for_meal_plan"] >= 1

    def test_ingredient_already_in_inventory_not_added(self):
        from chatbot.tools.shopping import get_shopping_list
        items = [{"display_name": "Pasta", "quantity": 500, "unit": "g", "status": "fresh"}]
        plan = {
            "success": True,
            "data": {
                "meals": {
                    "Monday": {
                        "dinner": [{"meal_name": "Pasta", "ingredients": ["Pasta"]}]
                    }
                }
            }
        }
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_meal_plan", return_value=plan),
        ):
            result = get_shopping_list("u1")
        assert result["summary"]["needed_for_meal_plan"] == 0

    def test_exception_returns_failure(self):
        from chatbot.tools.shopping import get_shopping_list
        with patch(f"{_MOD}.get_profile", side_effect=RuntimeError("crash")):
            result = get_shopping_list("u1")
        assert result["success"] is False

    def test_household_size_from_profile(self):
        from chatbot.tools.shopping import get_shopping_list
        with (
            patch(f"{_MOD}.get_profile", return_value={"household_size": 4}),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": []}),
            patch(f"{_MOD}.get_meal_plan", return_value={"success": True, "data": {"meals": {}}}),
        ):
            result = get_shopping_list("u1")
        assert result["household_size"] == 4
