"""Tests for services/shelf_life_service.py."""
import pytest
from unittest.mock import patch, call

_SVC = "services.shelf_life_service"


class TestFetchShelfLife:
    def test_returns_shelf_life_days_when_doc_found(self):
        from services.shelf_life_service import fetch_shelf_life
        with patch(f"{_SVC}.get_shelf_life_doc", return_value={"shelf_life_days": 14}):
            result = fetch_shelf_life("Milk")
        assert result == 14

    def test_returns_none_when_no_doc(self):
        from services.shelf_life_service import fetch_shelf_life
        with patch(f"{_SVC}.get_shelf_life_doc", return_value=None):
            result = fetch_shelf_life("Unknown Item")
        assert result is None

    def test_key_is_normalised_to_lowercase(self):
        from services.shelf_life_service import fetch_shelf_life
        with patch(f"{_SVC}.get_shelf_life_doc", return_value=None) as mock_get:
            fetch_shelf_life("  CHICKEN  ")
        mock_get.assert_called_once_with("chicken")

    def test_key_strips_whitespace(self):
        from services.shelf_life_service import fetch_shelf_life
        with patch(f"{_SVC}.get_shelf_life_doc", return_value={"shelf_life_days": 3}) as mock_get:
            fetch_shelf_life("  spinach  ")
        mock_get.assert_called_once_with("spinach")


class TestStoreShelfLife:
    def test_stores_with_normalised_key(self):
        from services.shelf_life_service import store_shelf_life
        with (
            patch(f"{_SVC}.upsert_shelf_life") as mock_upsert,
            patch(f"{_SVC}.now_ist") as mock_now,
        ):
            mock_now.return_value.isoformat.return_value = "2024-01-15T12:00:00"
            store_shelf_life("  EGGS  ", 21)
        mock_upsert.assert_called_once_with(
            item_key="eggs",
            shelf_life_days=21,
            updated_at="2024-01-15T12:00:00",
        )


class TestGetShelfLife:
    def test_cache_hit_returns_cached_value_without_calling_generate(self):
        from services.shelf_life_service import get_shelf_life
        with (
            patch(f"{_SVC}.get_shelf_life_doc", return_value={"shelf_life_days": 7}),
            patch(f"{_SVC}.generate_shelf_life") as mock_gen,
        ):
            result = get_shelf_life("milk")
        assert result == 7
        mock_gen.assert_not_called()

    def test_cache_miss_calls_generate_and_stores(self):
        from services.shelf_life_service import get_shelf_life
        with (
            patch(f"{_SVC}.get_shelf_life_doc", return_value=None),
            patch(f"{_SVC}.generate_shelf_life", return_value=30) as mock_gen,
            patch(f"{_SVC}.upsert_shelf_life") as mock_upsert,
            patch(f"{_SVC}.now_ist") as mock_now,
        ):
            mock_now.return_value.isoformat.return_value = "2024-01-15T12:00:00"
            result = get_shelf_life("avocado")
        assert result == 30
        mock_gen.assert_called_once_with("avocado")
        mock_upsert.assert_called_once()

    def test_cache_miss_returns_generated_value(self):
        from services.shelf_life_service import get_shelf_life
        with (
            patch(f"{_SVC}.get_shelf_life_doc", return_value=None),
            patch(f"{_SVC}.generate_shelf_life", return_value=14),
            patch(f"{_SVC}.upsert_shelf_life"),
            patch(f"{_SVC}.now_ist") as mock_now,
        ):
            mock_now.return_value.isoformat.return_value = "2024-01-15T12:00:00"
            result = get_shelf_life("broccoli")
        assert result == 14
