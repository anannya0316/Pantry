"""Tests for chatbot/tools/recipes.py."""
import pytest
from unittest.mock import patch

_MOD = "chatbot.tools.recipes"


class TestSuggestRecipes:
    def test_no_api_key_returns_failure(self):
        from chatbot.tools.recipes import suggest_recipes
        with patch(f"{_MOD}.get_api_key", return_value=None):
            result = suggest_recipes("u1")
        assert result["success"] is False
        assert "unavailable" in result["error"].lower()

    def test_no_inventory_returns_failure(self):
        from chatbot.tools.recipes import suggest_recipes
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value=None),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is False
        assert "No inventory" in result["error"]

    def test_empty_inventory_returns_failure(self):
        from chatbot.tools.recipes import suggest_recipes
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": []}),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_all_zero_quantity_items_treated_as_empty(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Milk", "quantity": 0, "unit": "liter"}]
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is False

    def test_successful_recipe_suggestion(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Eggs", "quantity": 6, "unit": "pieces"}]
        recipes = [{"name": "Scrambled Eggs", "ingredients": ["Eggs"]}]
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.load_prompt", return_value="{inventory}\n{household_size}\n{preferences_line}"),
            patch(f"{_MOD}.call_llm", return_value='[{"name": "Scrambled Eggs"}]'),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is True
        assert len(result["recipes"]) == 1

    def test_strips_markdown_fences_from_llm_response(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Tomato", "quantity": 3, "unit": "pieces"}]
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.load_prompt", return_value="{inventory}\n{household_size}\n{preferences_line}"),
            patch(f"{_MOD}.call_llm", return_value='```json\n[{"name": "Tomato Soup"}]\n```'),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is True

    def test_non_list_llm_response_returns_failure(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Rice", "quantity": 1, "unit": "kg"}]
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.load_prompt", return_value="{inventory}\n{household_size}\n{preferences_line}"),
            patch(f"{_MOD}.call_llm", return_value='{"error": "could not generate"}'),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is False
        assert "format" in result["error"].lower()

    def test_llm_exception_returns_failure(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Chicken", "quantity": 1, "unit": "kg"}]
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.load_prompt", return_value="{inventory}\n{household_size}\n{preferences_line}"),
            patch(f"{_MOD}.call_llm", side_effect=RuntimeError("timeout")),
        ):
            result = suggest_recipes("u1")
        assert result["success"] is False

    def test_preferences_passed_to_prompt(self):
        from chatbot.tools.recipes import suggest_recipes
        items = [{"display_name": "Tofu", "quantity": 1, "unit": "kg"}]
        captured_prompt = []
        def mock_llm(prompt, **kwargs):
            captured_prompt.append(prompt)
            return '[{"name": "Tofu Stir Fry"}]'
        with (
            patch(f"{_MOD}.get_api_key", return_value="sk-test"),
            patch(f"{_MOD}.get_user_inventory", return_value={"items": items}),
            patch(f"{_MOD}.get_profile", return_value={"household_size": 2}),
            patch(f"{_MOD}.load_prompt", return_value="{inventory}\n{household_size}\n{preferences_line}"),
            patch(f"{_MOD}.call_llm", side_effect=mock_llm),
        ):
            suggest_recipes("u1", preferences="vegan")
        assert "vegan" in captured_prompt[0]
