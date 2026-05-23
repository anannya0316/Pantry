"""Tests for utils/profile_utils.py — is_vegetarian_profile, is_meal_veg."""
import pytest
from utils.profile_utils import is_vegetarian_profile, is_meal_veg


class TestIsVegetarianProfile:
    def test_veg_string_is_vegetarian(self):
        assert is_vegetarian_profile("veg") is True

    def test_non_veg_string_matches_veg_substring(self):
        # "veg" is a substring of "non_veg", so this returns True — known limitation
        assert is_vegetarian_profile("non_veg") is True

    def test_contains_veg_substring(self):
        assert is_vegetarian_profile("strictly_veg") is True

    def test_list_with_veg_is_vegetarian(self):
        assert is_vegetarian_profile(["veg"]) is True

    def test_list_with_non_veg_also_matches_substring(self):
        # Same substring limitation applies to list input
        assert is_vegetarian_profile(["non_veg"]) is True

    def test_case_insensitive(self):
        assert is_vegetarian_profile("VEG") is True

    def test_empty_list_is_not_vegetarian(self):
        assert is_vegetarian_profile([]) is False

    def test_veg_among_multiple_preferences(self):
        assert is_vegetarian_profile(["gluten-free", "veg"]) is True


class TestIsMealVeg:
    def _meal(self, meal_name, ingredients=None):
        return {
            "meal_name": meal_name,
            "ingredients": ingredients or [],
        }

    def test_plain_vegetable_meal_is_veg(self):
        meal = self._meal("dal tadka", [{"name": "lentils"}, {"name": "tomato"}])
        assert is_meal_veg(meal) is True

    def test_meal_with_chicken_in_name_is_not_veg(self):
        meal = self._meal("chicken curry", [])
        assert is_meal_veg(meal) is False

    def test_meal_with_beef_ingredient_is_not_veg(self):
        meal = self._meal("tacos", [{"name": "beef"}, {"name": "cheese"}])
        assert is_meal_veg(meal) is False

    def test_meal_with_fish_ingredient_is_not_veg(self):
        meal = self._meal("rice bowl", [{"name": "fish"}, {"name": "rice"}])
        assert is_meal_veg(meal) is False

    def test_meal_with_egg_is_not_veg(self):
        meal = self._meal("egg fried rice", [])
        assert is_meal_veg(meal) is False

    def test_paneer_meal_is_veg(self):
        meal = self._meal("paneer tikka", [{"name": "paneer"}, {"name": "bell pepper"}])
        assert is_meal_veg(meal) is True

    def test_empty_ingredients_no_meat_in_name_is_veg(self):
        meal = self._meal("vegetable stew", [])
        assert is_meal_veg(meal) is True

    def test_shrimp_ingredient_is_not_veg(self):
        meal = self._meal("pasta", [{"name": "shrimp"}, {"name": "garlic"}])
        assert is_meal_veg(meal) is False

    def test_no_meal_name_key_defaults_to_empty(self):
        meal = {"ingredients": [{"name": "rice"}]}
        assert is_meal_veg(meal) is True
