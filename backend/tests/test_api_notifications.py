"""API route tests for /notifications endpoint."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.routes.notifications import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

_SVC = "api.routes.notifications"


class TestGetNotificationsRoute:
    def test_no_user_id_returns_empty_list(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_user_id_calls_service(self):
        notifications = [{"message": "Low stock: Milk", "type": "low_stock"}]
        with patch(f"{_SVC}.get_notifications", return_value=notifications):
            resp = client.get("/", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["type"] == "low_stock"

    def test_empty_notifications_returns_empty_list(self):
        with patch(f"{_SVC}.get_notifications", return_value=[]):
            resp = client.get("/", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json() == []
