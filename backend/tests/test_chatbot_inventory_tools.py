"""Tests for chatbot/tools/inventory.py — tool functions and _find_item helper."""
import pytest
from unittest.mock import patch, MagicMock

_MOD = "chatbot.tools.inventory"


# ---------------------------------------------------------------------------
# _find_item helper
# ---------------------------------------------------------------------------

class TestFindItem:
    def _call(self, items, input_name):
        from chatbot.tools.inventory import _find_item
        return _find_item(items, input_name)

    def test_exact_match_by_display_name(self):
        items = [{"display_name": "Milk", "aliases": []}]
        idx, item = self._call(items, "milk")
        assert idx == 0
        assert item["display_name"] == "Milk"

    def test_alias_match(self):
        items = [{"display_name": "Full Fat Milk", "aliases": ["milk", "whole milk"]}]
        idx, item = self._call(items, "milk")
        assert idx == 0

    def test_fuzzy_match_fallback(self):
        items = [{"display_name": "Tomatoes", "aliases": []}]
        idx, item = self._call(items, "tomato")
        assert idx == 0

    def test_no_match_returns_none_none(self):
        items = [{"display_name": "Milk", "aliases": []}]
        idx, item = self._call(items, "xyz_unknown_item_12345")
        assert idx is None
        assert item is None

    def test_empty_items_returns_none_none(self):
        idx, item = self._call([], "milk")
        assert idx is None
        assert item is None

    def test_index_order_preserved(self):
        items = [
            {"display_name": "Eggs", "aliases": []},
            {"display_name": "Milk", "aliases": []},
        ]
        idx, _ = self._call(items, "milk")
        assert idx == 1


# ---------------------------------------------------------------------------
# add_inventory_item
# ---------------------------------------------------------------------------

class TestAddInventoryItem:
    def test_empty_display_name_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "   ")
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_missing_quantity_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "Milk", quantity=None, unit="liter")
        assert result["success"] is False
        assert "quantity" in result["missing_fields"]

    def test_missing_unit_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "Milk", quantity=2, unit=None)
        assert result["success"] is False
        assert "unit" in result["missing_fields"]

    def test_zero_quantity_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "Milk", quantity=0, unit="liter")
        assert result["success"] is False
        assert "positive" in result["error"].lower()

    def test_negative_quantity_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "Milk", quantity=-1, unit="liter")
        assert result["success"] is False

    def test_invalid_unit_fails(self):
        from chatbot.tools.inventory import add_inventory_item
        result = add_inventory_item("u1", "Milk", quantity=2, unit="buckets")
        assert result["success"] is False
        assert "Invalid unit" in result["error"]

    def test_existing_item_updates_in_place(self):
        from chatbot.tools.inventory import add_inventory_item
        existing = [{"display_name": "Milk", "aliases": [], "category": "Dairy", "status": "fresh"}]
        with (
            patch(f"{_MOD}.get_user_inventory", return_value={"items": existing}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.update_inventory") as mock_update,
        ):
            result = add_inventory_item("u1", "milk", quantity=3, unit="liter")
        assert result["success"] is True
        mock_update.assert_called_once()

    def test_new_item_pushes_to_inventory(self):
        from chatbot.tools.inventory import add_inventory_item
        with (
            patch(f"{_MOD}.get_user_inventory", return_value={"items": []}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.classify_item", return_value={"display_name": "Butter", "category": "Dairy"}),
            patch(f"{_MOD}.push_inventory_items") as mock_push,
        ):
            result = add_inventory_item("u1", "Butter", quantity=200, unit="g")
        assert result["success"] is True
        mock_push.assert_called_once()

    def test_unexpected_exception_returns_failure(self):
        from chatbot.tools.inventory import add_inventory_item
        with patch(f"{_MOD}.get_user_inventory", side_effect=RuntimeError("DB down")):
            result = add_inventory_item("u1", "Milk", quantity=1, unit="liter")
        assert result["success"] is False
        assert "Unexpected error" in result["error"]


# ---------------------------------------------------------------------------
# update_inventory_item
# ---------------------------------------------------------------------------

class TestUpdateInventoryItem:
    def test_empty_display_name_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        result = update_inventory_item("u1", "  ")
        assert result["success"] is False

    def test_no_inventory_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        with patch(f"{_MOD}.get_user_inventory", return_value=None):
            result = update_inventory_item("u1", "Milk")
        assert result["success"] is False
        assert "Inventory not found" in result["error"]

    def test_item_not_found_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        with patch(f"{_MOD}.get_user_inventory", return_value={"items": []}):
            result = update_inventory_item("u1", "Milk")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_no_fields_provided_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        items = [{"display_name": "Milk", "aliases": []}]
        with patch(f"{_MOD}.get_user_inventory", return_value={"items": items}):
            result = update_inventory_item("u1", "Milk")
        assert result["success"] is False
        assert "No fields" in result["error"]

    def test_negative_quantity_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        items = [{"display_name": "Milk", "aliases": []}]
        with patch(f"{_MOD}.get_user_inventory", return_value={"items": items}):
            result = update_inventory_item("u1", "Milk", quantity=-5)
        assert result["success"] is False
        assert "negative" in result["error"].lower()

    def test_invalid_unit_fails(self):
        from chatbot.tools.inventory import update_inventory_item
        items = [{"display_name": "Milk", "aliases": []}]
        with patch(f"{_MOD}.get_user_inventory", return_value={"items": items}):
            result = update_inventory_item("u1", "Milk", unit="barrels")
        assert result["success"] is False

    def test_successful_update(self):
        from chatbot.tools.inventory import update_inventory_item
        items = [{"display_name": "Milk", "aliases": [], "quantity": 1, "unit": "liter"}]
        with (
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.update_inventory"),
        ):
            result = update_inventory_item("u1", "Milk", quantity=3)
        assert result["success"] is True
        assert result["updated_fields"]["quantity"] == 3


# ---------------------------------------------------------------------------
# get_all_inventory_items
# ---------------------------------------------------------------------------

class TestGetAllInventoryItems:
    def test_no_inventory_returns_empty_list(self):
        from chatbot.tools.inventory import get_all_inventory_items
        with patch(f"{_MOD}.get_user_inventory", return_value=None):
            result = get_all_inventory_items("u1")
        assert result["success"] is True
        assert result["items"] == []

    def test_returns_items_from_inventory(self):
        from chatbot.tools.inventory import get_all_inventory_items
        items = [{"display_name": "Milk"}, {"display_name": "Eggs"}]
        with patch(f"{_MOD}.get_user_inventory", return_value={"items": items}):
            result = get_all_inventory_items("u1")
        assert result["success"] is True
        assert len(result["items"]) == 2

    def test_exception_returns_failure(self):
        from chatbot.tools.inventory import get_all_inventory_items
        with patch(f"{_MOD}.get_user_inventory", side_effect=RuntimeError("timeout")):
            result = get_all_inventory_items("u1")
        assert result["success"] is False
