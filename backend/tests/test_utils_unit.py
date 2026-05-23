"""Tests for utils/unit_utils.py."""
import pytest
from utils.unit_utils import normalize_unit, VALID_UNITS, UNIT_MAP


class TestNormalizeUnit:
    @pytest.mark.parametrize("unit", list(VALID_UNITS))
    def test_valid_units_pass_through(self, unit):
        assert normalize_unit(unit) == unit

    def test_valid_unit_with_whitespace(self):
        assert normalize_unit("  kg  ") == "kg"

    def test_valid_unit_uppercase(self):
        assert normalize_unit("KG") == "kg"

    def test_cup_maps_to_ml(self):
        assert normalize_unit("cup") == "ml"

    def test_cups_maps_to_ml(self):
        assert normalize_unit("cups") == "ml"

    def test_tablespoon_maps_to_ml(self):
        assert normalize_unit("tablespoon") == "ml"

    def test_tbsp_maps_to_ml(self):
        assert normalize_unit("tbsp") == "ml"

    def test_tsp_maps_to_ml(self):
        assert normalize_unit("tsp") == "ml"

    def test_teaspoon_maps_to_ml(self):
        assert normalize_unit("teaspoon") == "ml"

    def test_litre_maps_to_liter(self):
        assert normalize_unit("litre") == "liter"

    def test_l_maps_to_liter(self):
        assert normalize_unit("l") == "liter"

    def test_gram_maps_to_g(self):
        assert normalize_unit("gram") == "g"

    def test_grams_maps_to_g(self):
        assert normalize_unit("grams") == "g"

    def test_kilogram_maps_to_kg(self):
        assert normalize_unit("kilogram") == "kg"

    def test_lb_maps_to_lbs(self):
        assert normalize_unit("lb") == "lbs"

    def test_pound_maps_to_lbs(self):
        assert normalize_unit("pound") == "lbs"

    def test_oz_maps_to_g(self):
        assert normalize_unit("oz") == "g"

    def test_ounce_maps_to_g(self):
        assert normalize_unit("ounce") == "g"

    def test_piece_maps_to_pieces(self):
        assert normalize_unit("piece") == "pieces"

    def test_slice_maps_to_pieces(self):
        assert normalize_unit("slice") == "pieces"

    def test_bunch_maps_to_unit(self):
        assert normalize_unit("bunch") == "unit"

    def test_clove_maps_to_pieces(self):
        assert normalize_unit("clove") == "pieces"

    def test_loaves_maps_to_loaf(self):
        assert normalize_unit("loaves") == "loaf"

    def test_unknown_unit_falls_back_to_unit(self):
        assert normalize_unit("sprinkle") == "unit"

    def test_empty_string_falls_back_to_unit(self):
        assert normalize_unit("") == "unit"

    @pytest.mark.parametrize("alias, expected", list(UNIT_MAP.items()))
    def test_all_aliases_in_unit_map(self, alias, expected):
        assert normalize_unit(alias) == expected
