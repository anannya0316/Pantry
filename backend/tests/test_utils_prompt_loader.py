"""Tests for utils/prompt_loader.py — uses real prompt files in backend/prompts/."""
import pytest
from pathlib import Path


class TestLoadPrompt:
    def test_loads_shelf_life_prompt(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("shelf_life.txt")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_loads_classify_prompt(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("classify.txt")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_loads_nutrition_prompt(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("nutrition.txt")
        assert isinstance(result, str)

    def test_loads_low_stock_prompt(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("low_stock.txt")
        assert isinstance(result, str)

    def test_nonexistent_file_raises_file_not_found(self):
        from utils.prompt_loader import load_prompt
        with pytest.raises(FileNotFoundError):
            load_prompt("does_not_exist_xyz.txt")

    def test_returns_utf8_string(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("shelf_life.txt")
        result.encode("utf-8")

    def test_ingredient_extraction_prompt_loadable(self):
        from utils.prompt_loader import load_prompt
        result = load_prompt("ingredient_extraction.txt")
        assert isinstance(result, str)
        assert len(result) > 0
