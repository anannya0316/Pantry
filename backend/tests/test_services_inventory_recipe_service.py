"""Tests for services/inventory_recipe_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

_SVC = "services.inventory_recipe_service"


def _req(have=None, need_to_buy=None, ingredients=None):
    req = MagicMock()
    req.have = have or []
    req.need_to_buy = need_to_buy or []
    req.ingredients = ingredients or []
    return req


def _ing(name, quantity=1, unit="g"):
    ing = MagicMock()
    ing.name = name
    ing.quantity = quantity
    ing.unit = unit
    return ing


class TestUseRecipe:
    def test_no_user_id_raises_400(self):
        from services.inventory_recipe_service import use_recipe
        with pytest.raises(HTTPException) as exc:
            use_recipe(_req(), MagicMock(), None)
        assert exc.value.status_code == 400

    def test_inventory_not_found_raises_404(self):
        from services.inventory_recipe_service import use_recipe
        with patch(f"{_SVC}.get_user_inventory", return_value=None):
            with pytest.raises(HTTPException) as exc:
                use_recipe(_req(), MagicMock(), "u1")
        assert exc.value.status_code == 404

    def test_have_items_deducted_from_inventory(self):
        from services.inventory_recipe_service import use_recipe
        ing = _ing("tomato", 100, "g")
        req = _req(have=["tomato"], ingredients=[ing])
        inventory = {"items": [{"display_name": "Tomato", "quantity": 500, "unit": "g"}]}
        with (
            patch(f"{_SVC}.get_user_inventory", return_value=inventory),
            patch(f"{_SVC}.update_inventory_fields") as mock_update,
            patch(f"{_SVC}.push_inventory_items"),
            patch(f"{_SVC}.normalize_unit", return_value="g"),
        ):
            result = use_recipe(req, MagicMock(), "u1")
        assert result["adjusted"] == 1
        mock_update.assert_called_once()

    def test_need_to_buy_adds_new_items(self):
        from services.inventory_recipe_service import use_recipe
        ing = _ing("spinach", 200, "g")
        req = _req(need_to_buy=["spinach"], ingredients=[ing])
        inventory = {"items": []}
        with (
            patch(f"{_SVC}.get_user_inventory", return_value=inventory),
            patch(f"{_SVC}.update_inventory_fields"),
            patch(f"{_SVC}.push_inventory_items") as mock_push,
            patch(f"{_SVC}.normalize_unit", return_value="g"),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            result = use_recipe(req, MagicMock(), "u1")
        assert result["added"] == 1
        mock_push.assert_called_once()

    def test_existing_item_not_re_added(self):
        from services.inventory_recipe_service import use_recipe
        req = _req(need_to_buy=["tomato"])
        inventory = {"items": [{"display_name": "Tomato", "quantity": 5, "unit": "unit"}]}
        with (
            patch(f"{_SVC}.get_user_inventory", return_value=inventory),
            patch(f"{_SVC}.update_inventory_fields"),
            patch(f"{_SVC}.push_inventory_items") as mock_push,
            patch(f"{_SVC}.normalize_unit", return_value="unit"),
        ):
            result = use_recipe(req, MagicMock(), "u1")
        assert result["added"] == 0
        mock_push.assert_not_called()

    def test_empty_request_returns_zero_counts(self):
        from services.inventory_recipe_service import use_recipe
        inventory = {"items": [{"display_name": "Rice", "quantity": 500, "unit": "g"}]}
        with (
            patch(f"{_SVC}.get_user_inventory", return_value=inventory),
            patch(f"{_SVC}.update_inventory_fields") as mock_update,
            patch(f"{_SVC}.push_inventory_items") as mock_push,
        ):
            result = use_recipe(_req(), MagicMock(), "u1")
        assert result["adjusted"] == 0
        assert result["added"] == 0
        mock_update.assert_not_called()
        mock_push.assert_not_called()

    def test_unit_mismatch_deducts_one(self):
        from services.inventory_recipe_service import use_recipe
        ing = _ing("salt", 2, "tsp")
        req = _req(have=["salt"], ingredients=[ing])
        inventory = {"items": [{"display_name": "Salt", "quantity": 500, "unit": "g"}]}
        with (
            patch(f"{_SVC}.get_user_inventory", return_value=inventory),
            patch(f"{_SVC}.update_inventory_fields") as mock_update,
            patch(f"{_SVC}.push_inventory_items"),
            patch(f"{_SVC}.normalize_unit", return_value="tsp"),
        ):
            result = use_recipe(req, MagicMock(), "u1")
        assert result["adjusted"] == 1
        updates = mock_update.call_args[0][1]
        assert updates["items.0.quantity"] == 499
