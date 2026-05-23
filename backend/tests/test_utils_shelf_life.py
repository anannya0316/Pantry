"""Tests for utils/shelf_life_utils.py."""
import pytest
from utils.shelf_life_utils import extract_shelf_life_days
from constants.shelf_life_constants import DEFAULT_SHELF_LIFE_DAYS


class TestExtractShelfLifeDays:
    def test_simple_integer_response(self):
        assert extract_shelf_life_days("7") == 7

    def test_number_embedded_in_sentence(self):
        assert extract_shelf_life_days("This item lasts about 14 days.") == 14

    def test_extracts_first_number(self):
        assert extract_shelf_life_days("3 to 5 days") == 3

    def test_large_number(self):
        assert extract_shelf_life_days("365 days in a year") == 365

    def test_no_number_returns_default(self):
        assert extract_shelf_life_days("indefinite") == DEFAULT_SHELF_LIFE_DAYS

    def test_empty_string_returns_default(self):
        assert extract_shelf_life_days("") == DEFAULT_SHELF_LIFE_DAYS

    def test_whitespace_only_returns_default(self):
        assert extract_shelf_life_days("   ") == DEFAULT_SHELF_LIFE_DAYS

    def test_leading_number(self):
        assert extract_shelf_life_days("30 days shelf life") == 30

    def test_multi_digit_number(self):
        assert extract_shelf_life_days("Shelf life is approximately 180 days.") == 180

    def test_returns_int_not_float(self):
        result = extract_shelf_life_days("10 days")
        assert isinstance(result, int)
