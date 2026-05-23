"""Tests for services/inventory_service.py.

DB calls and classification are mocked; only service logic is tested.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Patch heavy imports before importing the module under test
_DAO_PATH = "services.inventory_service"


def _make_request(**kwargs):
    """Minimal mock of an inventory request object."""
    obj = MagicMock()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# classify_inventory_item
# ---------------------------------------------------------------------------

class TestClassifyInventoryItem:
    def test_raises_400_when_no_user_id(self):
        from services.inventory_service import classify_inventory_item
        req = _make_request(display_name="Milk")
        with pytest.raises(HTTPException) as exc_info:
            classify_inventory_item(req, user_id=None)
        assert exc_info.value.status_code == 400

    def test_calls_classify_and_returns_result(self):
        from services.inventory_service import classify_inventory_item
        req = _make_request(display_name="Milk")
        mock_classified = {"display_name": "Milk", "category": "Dairy"}
        with (
            patch(f"{_DAO_PATH}.get_user", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.classify_item", return_value=mock_classified) as mock_cls,
        ):
            result = classify_inventory_item(req, user_id="u1")
        mock_cls.assert_called_once_with("Milk", 2)
        assert result == mock_classified

    def test_missing_user_uses_default_household_size_1(self):
        from services.inventory_service import classify_inventory_item
        req = _make_request(display_name="Eggs")
        with (
            patch(f"{_DAO_PATH}.get_user", return_value=None),
            patch(f"{_DAO_PATH}.classify_item", return_value={}) as mock_cls,
        ):
            classify_inventory_item(req, user_id="u1")
        mock_cls.assert_called_once_with("Eggs", 1)

    def test_classification_error_raises_500(self):
        from services.inventory_service import classify_inventory_item
        req = _make_request(display_name="Milk")
        with (
            patch(f"{_DAO_PATH}.get_user", return_value={}),
            patch(f"{_DAO_PATH}.classify_item", side_effect=RuntimeError("LLM down")),
        ):
            with pytest.raises(HTTPException) as exc_info:
                classify_inventory_item(req, user_id="u1")
        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# get_inventory
# ---------------------------------------------------------------------------

class TestGetInventory:
    def test_no_user_id_raises_400(self):
        from services.inventory_service import get_inventory
        with pytest.raises(HTTPException) as exc_info:
            get_inventory(user_id=None)
        assert exc_info.value.status_code == 400

    def test_no_inventory_doc_returns_empty_list(self):
        from services.inventory_service import get_inventory
        with patch(f"{_DAO_PATH}.get_user_inventory", return_value=None):
            result = get_inventory("u1")
        assert result == []

    def test_enriches_and_returns_items(self):
        from services.inventory_service import get_inventory
        items = [{"display_name": "Milk", "quantity": 1, "unit": "liter"}]
        enriched = [{"display_name": "Milk", "quantity": 1, "unit": "liter", "shelf_life_days": 7}]
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": items}),
            patch("services.inventory_service.enrich_with_shelf_life", return_value=enriched),
        ):
            result = get_inventory("u1")
        assert result == enriched


# ---------------------------------------------------------------------------
# update_inventory_item
# ---------------------------------------------------------------------------

class TestUpdateInventoryItem:
    def test_raises_400_when_no_user_id(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=0, display_name="Milk", quantity=2, unit="liter",
                            category="Dairy", purchase_date=None)
        with pytest.raises(HTTPException) as exc_info:
            update_inventory_item(req, user_id=None)
        assert exc_info.value.status_code == 400

    def test_raises_404_when_no_inventory(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=0, display_name="Milk", quantity=2, unit="liter",
                            category="Dairy", purchase_date=None)
        with patch(f"{_DAO_PATH}.get_user_inventory", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                update_inventory_item(req, user_id="u1")
        assert exc_info.value.status_code == 404

    def test_raises_400_for_invalid_index(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=5, display_name="Milk", quantity=2, unit="liter",
                            category="Dairy", purchase_date=None)
        with patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": [{"display_name": "Eggs"}]}):
            with pytest.raises(HTTPException) as exc_info:
                update_inventory_item(req, user_id="u1")
        assert exc_info.value.status_code == 400

    def test_negative_index_raises_400(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=-1, display_name="Milk", quantity=2, unit="liter",
                            category="Dairy", purchase_date=None)
        with patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": [{"display_name": "Eggs"}]}):
            with pytest.raises(HTTPException) as exc_info:
                update_inventory_item(req, user_id="u1")
        assert exc_info.value.status_code == 400

    def test_success_returns_updated_message(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=0, display_name="Full Fat Milk", quantity=2,
                            unit="liter", category="Dairy", purchase_date=None)
        mock_result = MagicMock()
        mock_result.modified_count = 1
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": [{"display_name": "Milk", "status": "fresh"}]}),
            patch(f"{_DAO_PATH}.update_inventory_item_by_index", return_value=mock_result),
        ):
            result = update_inventory_item(req, user_id="u1")
        assert result["message"] == "Item updated successfully"

    def test_no_change_returns_no_changes_message(self):
        from services.inventory_service import update_inventory_item
        req = _make_request(index=0, display_name="Milk", quantity=1,
                            unit="liter", category="Dairy", purchase_date=None)
        mock_result = MagicMock()
        mock_result.modified_count = 0
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": [{"display_name": "Milk", "status": "fresh"}]}),
            patch(f"{_DAO_PATH}.update_inventory_item_by_index", return_value=mock_result),
        ):
            result = update_inventory_item(req, user_id="u1")
        assert "No changes" in result["message"]


# ---------------------------------------------------------------------------
# add_inventory_items
# ---------------------------------------------------------------------------

class TestAddInventoryItems:
    def _make_item(self, display_name, quantity=1, unit="unit", purchase_date=None):
        item = MagicMock()
        item.display_name = display_name
        item.quantity = quantity
        item.unit = unit
        item.purchase_date = purchase_date
        return item

    def test_raises_400_when_no_user_id(self):
        from services.inventory_service import add_inventory_items
        req = _make_request(items=[self._make_item("Milk")])
        with pytest.raises(HTTPException) as exc_info:
            add_inventory_items(req, background_tasks=MagicMock(), user_id=None)
        assert exc_info.value.status_code == 400

    def test_duplicate_item_raises_409(self):
        from services.inventory_service import add_inventory_items
        existing = [{"display_name": "Milk", "aliases": []}]
        req = _make_request(items=[self._make_item("Milk")])
        classified = {"display_name": "Milk", "category": "Dairy", "quantity": 1, "unit": "liter"}
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": existing}),
            patch(f"{_DAO_PATH}.get_profile", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.classify_item", return_value=classified),
        ):
            with pytest.raises(HTTPException) as exc_info:
                add_inventory_items(req, background_tasks=MagicMock(), user_id="u1")
        assert exc_info.value.status_code == 409

    def test_new_item_added_successfully(self):
        from services.inventory_service import add_inventory_items
        req = _make_request(items=[self._make_item("Butter")])
        classified = {"display_name": "Butter", "category": "Dairy", "quantity": 200, "unit": "g"}
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": []}),
            patch(f"{_DAO_PATH}.get_profile", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.classify_item", return_value=classified),
            patch(f"{_DAO_PATH}.push_inventory_items") as mock_push,
            patch("services.inventory_service.get_shelf_life"),
        ):
            bg = MagicMock()
            result = add_inventory_items(req, background_tasks=bg, user_id="u1")
        assert result["count"] == 1
        assert result["message"] == "Items added successfully"
        mock_push.assert_called_once()

    def test_alias_duplicate_detected(self):
        from services.inventory_service import add_inventory_items
        existing = [{"display_name": "Full Fat Milk", "aliases": ["milk"]}]
        req = _make_request(items=[self._make_item("milk")])
        classified = {"display_name": "Full Fat Milk", "category": "Dairy", "quantity": 1, "unit": "liter"}
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": existing}),
            patch(f"{_DAO_PATH}.get_profile", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.classify_item", return_value=classified),
        ):
            with pytest.raises(HTTPException) as exc_info:
                add_inventory_items(req, background_tasks=MagicMock(), user_id="u1")
        assert exc_info.value.status_code == 409

    def test_no_existing_inventory_still_adds(self):
        from services.inventory_service import add_inventory_items
        req = _make_request(items=[self._make_item("Eggs")])
        classified = {"display_name": "Eggs", "category": "Protein", "quantity": 6, "unit": "pieces"}
        with (
            patch(f"{_DAO_PATH}.get_user_inventory", return_value=None),
            patch(f"{_DAO_PATH}.get_profile", return_value={"household_size": 1}),
            patch(f"{_DAO_PATH}.classify_item", return_value=classified),
            patch(f"{_DAO_PATH}.push_inventory_items"),
            patch("services.inventory_service.get_shelf_life"),
        ):
            result = add_inventory_items(req, background_tasks=MagicMock(), user_id="u1")
        assert result["count"] == 1


# ---------------------------------------------------------------------------
# reclassify_inventory
# ---------------------------------------------------------------------------

class TestReclassifyInventory:
    def test_raises_400_when_no_user_id(self):
        from services.inventory_service import reclassify_inventory
        with pytest.raises(HTTPException) as exc_info:
            reclassify_inventory(user_id=None)
        assert exc_info.value.status_code == 400

    def test_raises_404_when_user_not_found(self):
        from services.inventory_service import reclassify_inventory
        with patch(f"{_DAO_PATH}.get_user", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                reclassify_inventory(user_id="u1")
        assert exc_info.value.status_code == 404

    def test_no_inventory_returns_zero_count(self):
        from services.inventory_service import reclassify_inventory
        with (
            patch(f"{_DAO_PATH}.get_user", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.get_user_inventory", return_value=None),
        ):
            result = reclassify_inventory("u1")
        assert result["count"] == 0

    def test_updates_items_with_classifications(self):
        from services.inventory_service import reclassify_inventory
        items = [{"display_name": "milk", "category": "Other", "quantity": 1, "unit": "unit"}]
        classified = {"display_name": "Milk", "category": "Dairy", "quantity": 2, "unit": "liter"}
        with (
            patch(f"{_DAO_PATH}.get_user", return_value={"household_size": 2}),
            patch(f"{_DAO_PATH}.get_user_inventory", return_value={"items": items}),
            patch(f"{_DAO_PATH}.classify_item", return_value=classified),
            patch(f"{_DAO_PATH}.update_inventory") as mock_update,
        ):
            result = reclassify_inventory("u1")
        assert "Reclassified" in result["message"]
        mock_update.assert_called_once()
