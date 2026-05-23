"""API route tests for /inventory endpoints using FastAPI TestClient."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from api.routes.inventory import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.inventory"


class TestGetInventory:
    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.get_inventory", side_effect=HTTPException(400, "user_id header is required")):
            resp = client.get("/", headers={})
        assert resp.status_code == 400

    def test_returns_inventory_list(self):
        items = [{"display_name": "Milk", "quantity": 1, "unit": "liter", "shelf_life_days": 7}]
        with patch(f"{_SVC}.get_inventory", return_value=items):
            resp = client.get("/", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestClassifyEndpoint:
    def test_classify_returns_classification(self):
        classified = {"display_name": "Milk", "category": "Dairy"}
        with patch(f"{_SVC}.classify_inventory_item", return_value=classified):
            resp = client.post("/classify", json={"display_name": "milk"}, headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["category"] == "Dairy"

    def test_classify_no_user_id_400(self):
        with patch(f"{_SVC}.classify_inventory_item", side_effect=HTTPException(400, "user_id required")):
            resp = client.post("/classify", json={"display_name": "milk"})
        assert resp.status_code == 400


class TestReclassifyEndpoint:
    def test_reclassify_success(self):
        with patch(f"{_SVC}.reclassify_inventory", return_value={"message": "Reclassified 3 items"}):
            resp = client.post("/reclassify", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert "Reclassified" in resp.json()["message"]

    def test_reclassify_no_user_returns_400(self):
        with patch(f"{_SVC}.reclassify_inventory", side_effect=HTTPException(400, "user_id required")):
            resp = client.post("/reclassify")
        assert resp.status_code == 400


class TestUpdateInventoryEndpoint:
    def test_update_success(self):
        payload = {
            "index": 0, "display_name": "Milk",
            "quantity": 2, "unit": "liter",
            "category": "Dairy"
        }
        with patch(f"{_SVC}.update_inventory_item", return_value={"message": "Item updated successfully"}):
            resp = client.put("/update", json=payload, headers={"user-id": "u1"})
        assert resp.status_code == 200

    def test_update_invalid_index_returns_400(self):
        payload = {"index": 99, "display_name": "Milk", "quantity": 1, "unit": "liter"}
        with patch(f"{_SVC}.update_inventory_item", side_effect=HTTPException(400, "Invalid item index")):
            resp = client.put("/update", json=payload, headers={"user-id": "u1"})
        assert resp.status_code == 400


class TestAddInventoryEndpoint:
    def test_add_success(self):
        payload = {"items": [{"display_name": "Eggs", "quantity": 6, "unit": "pieces"}]}
        with patch(f"{_SVC}.add_inventory_items", return_value={"message": "Items added successfully", "count": 1}):
            resp = client.post("/add", json=payload, headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    def test_add_duplicate_returns_409(self):
        payload = {"items": [{"display_name": "Milk", "quantity": 1, "unit": "liter"}]}
        with patch(f"{_SVC}.add_inventory_items", side_effect=HTTPException(409, "You already have Milk")):
            resp = client.post("/add", json=payload, headers={"user-id": "u1"})
        assert resp.status_code == 409


class TestLowStockEndpoint:
    def test_returns_low_stock_list(self):
        low = [{"display_name": "Milk", "reason": "running low"}]
        with patch(f"{_SVC}.get_low_stock_items", return_value=low):
            resp = client.get("/low-stock", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
