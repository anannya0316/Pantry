"""API route tests for /shelf-life endpoint."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.routes.shelf_life import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.shelf_life"


class TestGetShelfLifeRoute:
    def test_missing_item_name_returns_400(self):
        resp = client.get("/", params={"item_name": ""})
        assert resp.status_code == 400

    def test_valid_item_returns_shelf_life(self):
        with patch(f"{_SVC}.get_shelf_life", return_value=7):
            resp = client.get("/", params={"item_name": "milk"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["item_name"] == "milk"
        assert body["shelf_life_days"] == 7

    def test_item_name_passed_to_service(self):
        captured = []
        def mock_get(name):
            captured.append(name)
            return 14
        with patch(f"{_SVC}.get_shelf_life", side_effect=mock_get):
            client.get("/", params={"item_name": "broccoli"})
        assert captured == ["broccoli"]
