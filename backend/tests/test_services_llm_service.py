"""Tests for services/llm_service.py."""
import pytest
from unittest.mock import patch

_SVC = "services.llm_service"


class TestGenerateShelfLife:
    def test_no_api_key_returns_default(self):
        from services.llm_service import generate_shelf_life
        from constants.shelf_life_constants import DEFAULT_SHELF_LIFE_DAYS
        with patch(f"{_SVC}.get_api_key", return_value=None):
            result = generate_shelf_life("milk")
        assert result == DEFAULT_SHELF_LIFE_DAYS

    def test_calls_llm_and_extracts_days(self):
        from services.llm_service import generate_shelf_life
        with (
            patch(f"{_SVC}.get_api_key", return_value="key123"),
            patch(f"{_SVC}.load_prompt", return_value="Shelf life of {item_name}?"),
            patch(f"{_SVC}.call_llm", return_value="7 days") as mock_llm,
            patch(f"{_SVC}.extract_shelf_life_days", return_value=7) as mock_extract,
        ):
            result = generate_shelf_life("milk")
        assert result == 7
        mock_extract.assert_called_once_with("7 days")

    def test_prompt_formatted_with_item_name(self):
        from services.llm_service import generate_shelf_life
        with (
            patch(f"{_SVC}.get_api_key", return_value="key123"),
            patch(f"{_SVC}.load_prompt", return_value="Item: {item_name}"),
            patch(f"{_SVC}.call_llm", return_value="14 days") as mock_llm,
            patch(f"{_SVC}.extract_shelf_life_days", return_value=14),
        ):
            generate_shelf_life("spinach")
        call_args = mock_llm.call_args[0][0]
        assert "spinach" in call_args

    def test_llm_exception_returns_default(self):
        from services.llm_service import generate_shelf_life
        from constants.shelf_life_constants import DEFAULT_SHELF_LIFE_DAYS
        with (
            patch(f"{_SVC}.get_api_key", return_value="key123"),
            patch(f"{_SVC}.load_prompt", return_value="Item: {item_name}"),
            patch(f"{_SVC}.call_llm", side_effect=Exception("timeout")),
        ):
            result = generate_shelf_life("milk")
        assert result == DEFAULT_SHELF_LIFE_DAYS

    def test_uses_low_temperature_for_llm(self):
        from services.llm_service import generate_shelf_life
        with (
            patch(f"{_SVC}.get_api_key", return_value="key"),
            patch(f"{_SVC}.load_prompt", return_value="Item: {item_name}"),
            patch(f"{_SVC}.call_llm", return_value="3") as mock_llm,
            patch(f"{_SVC}.extract_shelf_life_days", return_value=3),
        ):
            generate_shelf_life("bread")
        _, kwargs = mock_llm.call_args
        assert kwargs.get("temperature", 1) <= 0.2
