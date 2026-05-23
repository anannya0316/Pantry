"""Tests for utils/matching_utils.py."""
import pytest
from utils.matching_utils import normalize_text, fuzzy_match


class TestNormalizeText:
    def test_strips_leading_trailing_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_converts_to_lowercase(self):
        assert normalize_text("CHICKEN") == "chicken"

    def test_replaces_hyphens_with_spaces(self):
        assert normalize_text("stir-fry") == "stir fry"

    def test_combined_strip_lower_hyphen(self):
        assert normalize_text("  Brown-Rice  ") == "brown rice"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_no_changes_needed(self):
        assert normalize_text("plain text") == "plain text"

    def test_multiple_hyphens(self):
        assert normalize_text("home-made-bread") == "home made bread"


class TestFuzzyMatch:
    def test_exact_match_returns_true(self):
        assert fuzzy_match("chicken", "chicken") is True

    def test_case_insensitive_match(self):
        assert fuzzy_match("Chicken", "chicken") is True

    def test_hyphenated_vs_space(self):
        assert fuzzy_match("stir-fry", "stir fry") is True

    def test_clearly_different_strings_returns_false(self):
        assert fuzzy_match("chicken", "broccoli") is False

    def test_empty_first_string_returns_false(self):
        assert fuzzy_match("", "chicken") is False

    def test_empty_second_string_returns_false(self):
        assert fuzzy_match("chicken", "") is False

    def test_both_empty_returns_false(self):
        assert fuzzy_match("", "") is False

    def test_high_threshold_rejects_partial_match(self):
        assert fuzzy_match("chi", "chicken", threshold=90) is False

    def test_low_threshold_accepts_partial_match(self):
        assert fuzzy_match("chikn", "chicken", threshold=60) is True

    def test_default_threshold_80(self):
        # "tomato" vs "tomatoes" — very similar but not identical
        result = fuzzy_match("tomato", "tomatoes")
        # score should be around 92 — above 80
        assert result is True

    def test_similar_but_below_threshold_returns_false(self):
        # "chicken" vs "kitchen" — different enough at default 80
        result = fuzzy_match("chicken", "kitchen", threshold=95)
        assert result is False
