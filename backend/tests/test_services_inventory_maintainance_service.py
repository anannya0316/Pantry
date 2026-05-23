"""Tests for services/inventory_maintainance_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

_SVC = "services.inventory_maintainance_service"


class TestExpireStaleInventory:
    def test_no_inventory_doc_returns_early(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        with patch(f"{_SVC}.inventory_collection") as mock_inv:
            mock_inv.find_one.return_value = None
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_empty_items_returns_early(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        with patch(f"{_SVC}.inventory_collection") as mock_inv:
            mock_inv.find_one.return_value = {"items": []}
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_stale_item_zeroed(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        old_date = (date.today() - timedelta(days=20)).isoformat()
        items = [{"display_name": "Milk", "quantity": 2, "purchase_date": old_date}]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = [{"item_key": "milk", "shelf_life_days": 7}]
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_called_once()
        updates = mock_inv.update_one.call_args[0][1]["$set"]
        assert updates.get("items.0.quantity") == 0

    def test_fresh_item_not_zeroed(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        recent_date = date.today().isoformat()
        items = [{"display_name": "Yogurt", "quantity": 3, "purchase_date": recent_date}]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = [{"item_key": "yogurt", "shelf_life_days": 14}]
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_already_zero_quantity_not_updated(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        old_date = (date.today() - timedelta(days=30)).isoformat()
        items = [{"display_name": "Milk", "quantity": 0, "purchase_date": old_date}]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = [{"item_key": "milk", "shelf_life_days": 7}]
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_no_shelf_life_data_skips_item(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        old_date = (date.today() - timedelta(days=30)).isoformat()
        items = [{"display_name": "UnknownThing", "quantity": 5, "purchase_date": old_date}]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = []
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_no_purchase_date_skips_item(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        items = [{"display_name": "Rice", "quantity": 5}]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = [{"item_key": "rice", "shelf_life_days": 30}]
            expire_stale_inventory("u1")
        mock_inv.update_one.assert_not_called()

    def test_multiple_items_only_stale_ones_zeroed(self):
        from services.inventory_maintainance_service import expire_stale_inventory
        old = (date.today() - timedelta(days=20)).isoformat()
        fresh = date.today().isoformat()
        items = [
            {"display_name": "Milk", "quantity": 2, "purchase_date": old},
            {"display_name": "Rice", "quantity": 500, "purchase_date": fresh},
        ]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.shelf_life_collection") as mock_shelf,
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_shelf.find.return_value = [
                {"item_key": "milk", "shelf_life_days": 7},
                {"item_key": "rice", "shelf_life_days": 365},
            ]
            expire_stale_inventory("u1")
        updates = mock_inv.update_one.call_args[0][1]["$set"]
        assert "items.0.quantity" in updates
        assert "items.1.quantity" not in updates
