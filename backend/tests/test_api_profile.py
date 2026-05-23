"""API route tests for /profile endpoints."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from api.routes.profile import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.profile"


class TestGetProfileRoute:
    def test_returns_profile(self):
        profile = {"user_id": "u1", "name": "Alice", "household_size": 2}
        with patch(f"{_SVC}.get_user_profile", return_value=profile):
            resp = client.get("/", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice"

    def test_no_user_id_returns_error(self):
        with patch(f"{_SVC}.get_user_profile", side_effect=HTTPException(400, "user_id required")):
            resp = client.get("/")
        assert resp.status_code == 400

    def test_user_not_found_returns_404(self):
        with patch(f"{_SVC}.get_user_profile", side_effect=HTTPException(404, "not found")):
            resp = client.get("/", headers={"user-id": "ghost"})
        assert resp.status_code == 404


class TestUpdateGoalsRoute:
    def test_update_goals_success(self):
        with patch(f"{_SVC}.update_user_goals", return_value={"message": "Goals updated"}):
            resp = client.put(
                "/update-goals",
                json={"goals": ["Eat healthier"]},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200

    def test_update_goals_no_user_returns_400(self):
        with patch(f"{_SVC}.update_user_goals", side_effect=HTTPException(400, "user_id required")):
            resp = client.put("/update-goals", json={"goals": ["Eat healthier"]})
        assert resp.status_code == 400


class TestUpdateProfileRoute:
    def test_update_profile_success(self):
        with patch(f"{_SVC}.update_user_profile", return_value={"message": "Profile updated"}):
            resp = client.put(
                "/update",
                json={"household_size": 3},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200

    def test_update_profile_no_user_returns_400(self):
        with patch(f"{_SVC}.update_user_profile", side_effect=HTTPException(400, "user_id required")):
            resp = client.put("/update", json={"household_size": 3})
        assert resp.status_code == 400


class TestInsightsRoute:
    def test_returns_profile_insights(self):
        insights = {
            "health_alignment": 75,
            "health_alignment_sub": "Making good progress",
            "diet_balance": "Great",
            "diet_balance_sub": "Mostly balanced",
            "grocery_efficiency": 0,
            "grocery_efficiency_sub": "Stock up needed",
            "food_waste_risk": "Low",
            "food_waste_count": 1,
            "food_waste_sub": "1 item expiring soon",
        }
        with patch(f"{_SVC}.get_profile_insights", return_value=insights):
            resp = client.get("/insights", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["health_alignment"] == 75

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.get_profile_insights", side_effect=HTTPException(400, "user_id required")):
            resp = client.get("/insights")
        assert resp.status_code == 400
