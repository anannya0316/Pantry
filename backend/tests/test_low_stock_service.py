"""Tests for services/low_stock_service.py."""
import pytest
from datetime import date
from unittest.mock import patch

from services.low_stock_service import days_until, WEEKDAYS

_SVC = "services.low_stock_service"


# ---------------------------------------------------------------------------
# days_until (pure function — no mocking needed except today's date)
# ---------------------------------------------------------------------------

class TestDaysUntil:
    def _today_is(self, weekday_name: str):
        """Patch date.today() to return a specific weekday."""
        idx = WEEKDAYS.index(weekday_name)
        # 2024-01-01 is a Monday (weekday index 0)
        fixed = date(2024, 1, 1 + idx)
        return patch(f"{_SVC}.date")

    def test_same_day_returns_7(self):
        # If today == target day, next occurrence is 7 days away
        idx = date.today().weekday()
        today_name = WEEKDAYS[idx]
        result = days_until(today_name)
        assert result == 7

    def test_tomorrow_returns_1(self):
        idx = date.today().weekday()
        tomorrow_name = WEEKDAYS[(idx + 1) % 7]
        result = days_until(tomorrow_name)
        assert result == 1

    def test_yesterday_returns_6(self):
        idx = date.today().weekday()
        yesterday_name = WEEKDAYS[(idx - 1) % 7]
        result = days_until(yesterday_name)
        assert result == 6

    def test_result_always_between_1_and_7(self):
        for day in WEEKDAYS:
            result = days_until(day)
            assert 1 <= result <= 7


# ---------------------------------------------------------------------------
# get_low_stock_items (mocked DB + LLM)
# ---------------------------------------------------------------------------

class TestGetLowStockItems:
    def test_returns_empty_when_no_api_key(self):
        from services.low_stock_service import get_low_stock_items
        with patch(f"{_SVC}.get_api_key", return_value=None):
            result = get_low_stock_items("u1")
        assert result == []

    def test_returns_empty_when_no_inventory(self):
        from services.low_stock_service import get_low_stock_items
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value=None),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
        ):
            result = get_low_stock_items("u1")
        assert result == []

    def test_returns_empty_when_no_profile(self):
        from services.low_stock_service import get_low_stock_items
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": []}),
            patch(f"{_SVC}.get_profile", return_value=None),
        ):
            result = get_low_stock_items("u1")
        assert result == []

    def test_returns_empty_when_items_list_empty(self):
        from services.low_stock_service import get_low_stock_items
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": []}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
        ):
            result = get_low_stock_items("u1")
        assert result == []

    def test_parses_llm_json_response(self):
        from services.low_stock_service import get_low_stock_items
        items = [{"display_name": "Milk", "quantity": 0.5, "unit": "liter"}]
        llm_response = '[{"display_name": "Milk", "reason": "running low"}]'
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": items}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
            patch(f"{_SVC}.load_prompt", return_value="prompt: {today} {household_size} {grocery_shopping_day} {days_until_shopping} {inventory_json}"),
            patch(f"{_SVC}.call_llm", return_value=llm_response),
        ):
            result = get_low_stock_items("u1")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["display_name"] == "Milk"

    def test_handles_llm_error_gracefully(self):
        from services.low_stock_service import get_low_stock_items
        items = [{"display_name": "Rice", "quantity": 0.1, "unit": "kg"}]
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": items}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
            patch(f"{_SVC}.load_prompt", return_value="prompt: {today} {household_size} {grocery_shopping_day} {days_until_shopping} {inventory_json}"),
            patch(f"{_SVC}.call_llm", side_effect=RuntimeError("timeout")),
        ):
            result = get_low_stock_items("u1")
        assert result == []

    def test_handles_invalid_json_gracefully(self):
        from services.low_stock_service import get_low_stock_items
        items = [{"display_name": "Onion", "quantity": 1, "unit": "kg"}]
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": items}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
            patch(f"{_SVC}.load_prompt", return_value="prompt: {today} {household_size} {grocery_shopping_day} {days_until_shopping} {inventory_json}"),
            patch(f"{_SVC}.call_llm", return_value="not valid json at all"),
        ):
            result = get_low_stock_items("u1")
        assert result == []

    def test_strips_markdown_fences_from_llm_response(self):
        from services.low_stock_service import get_low_stock_items
        items = [{"display_name": "Eggs", "quantity": 2, "unit": "pieces"}]
        llm_response = '```json\n[{"display_name": "Eggs"}]\n```'
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": items}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
            patch(f"{_SVC}.load_prompt", return_value="prompt: {today} {household_size} {grocery_shopping_day} {days_until_shopping} {inventory_json}"),
            patch(f"{_SVC}.call_llm", return_value=llm_response),
        ):
            result = get_low_stock_items("u1")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_llm_returning_non_list_returns_empty(self):
        from services.low_stock_service import get_low_stock_items
        items = [{"display_name": "Butter", "quantity": 0.1, "unit": "kg"}]
        with (
            patch(f"{_SVC}.get_api_key", return_value="sk-test"),
            patch(f"{_SVC}.get_user_inventory", return_value={"items": items}),
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2, "grocery_shopping_day": "Sunday"}),
            patch(f"{_SVC}.load_prompt", return_value="prompt: {today} {household_size} {grocery_shopping_day} {days_until_shopping} {inventory_json}"),
            patch(f"{_SVC}.call_llm", return_value='{"error": "no low stock"}'),
        ):
            result = get_low_stock_items("u1")
        assert result == []
