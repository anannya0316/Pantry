"""Tests for services/classification_service.py."""
import json
import pytest
from unittest.mock import patch

_SVC = "services.classification_service"


def _json(display_name="tomato", category="Vegetables", quantity=1, unit="unit"):
    return json.dumps({
        "display_name": display_name,
        "category": category,
        "quantity": quantity,
        "unit": unit,
    })


class TestClassifyItem:
    def test_no_api_key_returns_other_category(self):
        from services.classification_service import classify_item
        with patch(f"{_SVC}.get_api_key", return_value=None):
            result = classify_item("tomato")
        assert result == {"category": "Other"}

    def test_llm_exception_returns_other(self):
        from services.classification_service import classify_item
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="classify {item_name} {household_size} {web_context}"),
            patch(f"{_SVC}.call_llm", side_effect=Exception("network error")),
        ):
            result = classify_item("tomato")
        assert result == {"category": "Other"}

    def test_success_returns_classified_item(self):
        from services.classification_service import classify_item
        llm_resp = _json("cherry tomato", "Vegetables", 500, "g")
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="classify {item_name} {household_size} {web_context}"),
            patch(f"{_SVC}.call_llm", return_value=llm_resp),
            patch(f"{_SVC}.tavily_search", return_value=""),
        ):
            result = classify_item("tomato", 2)
        assert result["category"] == "Vegetables"
        assert result["display_name"] == "cherry tomato"
        assert result["quantity"] == 500
        assert result["unit"] == "g"

    def test_unrecognized_name_triggers_web_search(self):
        from services.classification_service import classify_item
        first_resp = _json("tomato", "Vegetables", 1, "unit")
        second_resp = _json("roma tomato", "Vegetables", 2, "unit")
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="classify {item_name} {household_size} {web_context}"),
            patch(f"{_SVC}.call_llm", side_effect=[first_resp, second_resp]),
            patch(f"{_SVC}.tavily_search", return_value="tomato facts") as mock_tavily,
        ):
            result = classify_item("tomato", 2)
        mock_tavily.assert_called_once()
        assert result["display_name"] == "roma tomato"

    def test_recognized_name_skips_web_search(self):
        from services.classification_service import classify_item
        llm_resp = _json("cherry tomato", "Vegetables", 1, "unit")
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="classify {item_name} {household_size} {web_context}"),
            patch(f"{_SVC}.call_llm", return_value=llm_resp),
            patch(f"{_SVC}.tavily_search") as mock_tavily,
        ):
            classify_item("tomato", 2)
        mock_tavily.assert_not_called()

    def test_json_wrapped_in_codeblock_parsed_correctly(self):
        from services.classification_service import classify_item
        inner = json.dumps({"display_name": "spinach", "category": "Vegetables", "quantity": 200, "unit": "g"})
        llm_resp = f"```json\n{inner}\n```"
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="classify {item_name} {household_size} {web_context}"),
            patch(f"{_SVC}.call_llm", return_value=llm_resp),
            patch(f"{_SVC}.tavily_search", return_value=""),
        ):
            result = classify_item("spinach", 2)
        assert result["category"] == "Vegetables"
        assert result["display_name"] == "spinach"
