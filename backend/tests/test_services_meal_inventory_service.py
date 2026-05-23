"""Tests for services/meal_inventory_service.py."""
import pytest
from unittest.mock import patch

_SVC = "services.meal_inventory_service"


class TestFuzzyInventoryMatch:
    def test_exact_match(self):
        from services.meal_inventory_service import fuzzy_inventory_match
        assert fuzzy_inventory_match("tomato", "tomato") is True

    def test_similar_match(self):
        from services.meal_inventory_service import fuzzy_inventory_match
        assert fuzzy_inventory_match("tomatoes", "tomato") is True

    def test_no_match(self):
        from services.meal_inventory_service import fuzzy_inventory_match
        assert fuzzy_inventory_match("apple", "carrot") is False


class TestDeductIngredients:
    def _inv(self, name, qty, unit="g"):
        return {"display_name": name, "quantity": qty, "unit": unit}

    def test_matching_ingredient_deducted(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("tomato", 500, "g")]
        ingredients = [{"name": "tomato", "quantity": 100, "unit": "g"}]
        updates = deduct_ingredients(inventory, ingredients)
        assert "items.0.quantity" in updates
        assert updates["items.0.quantity"] == 400

    def test_no_match_returns_empty_updates(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("carrot", 300, "g")]
        ingredients = [{"name": "apple", "quantity": 50, "unit": "g"}]
        updates = deduct_ingredients(inventory, ingredients)
        assert updates == {}

    def test_unit_mismatch_deducts_one(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("flour", 1000, "g")]
        ingredients = [{"name": "flour", "quantity": 2, "unit": "cup"}]
        updates = deduct_ingredients(inventory, ingredients)
        assert updates["items.0.quantity"] == 999

    def test_quantity_never_below_zero(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("salt", 5, "g")]
        ingredients = [{"name": "salt", "quantity": 100, "unit": "g"}]
        updates = deduct_ingredients(inventory, ingredients)
        assert updates["items.0.quantity"] == 0

    def test_multiple_ingredients_updated_independently(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [
            self._inv("tomato", 500, "g"),
            self._inv("onion", 300, "g"),
        ]
        ingredients = [
            {"name": "tomato", "quantity": 100, "unit": "g"},
            {"name": "onion", "quantity": 50, "unit": "g"},
        ]
        updates = deduct_ingredients(inventory, ingredients)
        assert updates["items.0.quantity"] == 400
        assert updates["items.1.quantity"] == 250

    def test_inventory_updated_in_place(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("rice", 1000, "g")]
        ingredients = [{"name": "rice", "quantity": 200, "unit": "g"}]
        deduct_ingredients(inventory, ingredients)
        assert inventory[0]["quantity"] == 800

    def test_empty_ingredients_returns_empty_updates(self):
        from services.meal_inventory_service import deduct_ingredients
        inventory = [self._inv("rice", 500, "g")]
        updates = deduct_ingredients(inventory, [])
        assert updates == {}

    def test_empty_inventory_returns_empty_updates(self):
        from services.meal_inventory_service import deduct_ingredients
        updates = deduct_ingredients([], [{"name": "rice", "quantity": 100, "unit": "g"}])
        assert updates == {}
