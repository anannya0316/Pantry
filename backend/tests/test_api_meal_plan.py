"""API route tests for /meal-plan endpoints."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from api.routes.meal_plan import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.meal_plan"


class TestGetMealPlanRoute:
    def test_returns_meal_plan(self):
        plan = {"meals": {"Monday": {"breakfast": [], "lunch": [], "dinner": []}}}
        with patch(f"{_SVC}.get_meal_plan_service", return_value=plan):
            resp = client.get("/", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert "meals" in resp.json()

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.get_meal_plan_service", side_effect=HTTPException(400, "user_id required")):
            resp = client.get("/")
        assert resp.status_code == 400


class TestAddMealRoute:
    def test_add_meal_success(self):
        result = {"message": "Meal added successfully", "ingredients": ["Eggs", "Butter"]}
        with patch(f"{_SVC}.add_meal", return_value=result):
            resp = client.post(
                "/add",
                json={"day": "Monday", "meal_type": "breakfast", "meal_name": "Scrambled Eggs"},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Meal added successfully"

    def test_missing_body_fields_returns_422(self):
        resp = client.post("/add", json={"meal_name": "Eggs"}, headers={"user-id": "u1"})
        assert resp.status_code == 422

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.add_meal", side_effect=HTTPException(400, "user_id required")):
            resp = client.post(
                "/add",
                json={"day": "Monday", "meal_type": "breakfast", "meal_name": "Eggs"},
            )
        assert resp.status_code == 400


class TestDeleteMealRoute:
    def test_delete_meal_success(self):
        with patch(f"{_SVC}.delete_meal", return_value={"message": "Meal deleted"}):
            resp = client.post(
                "/delete",
                json={"day": "Monday", "meal_type": "breakfast"},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_missing_body_returns_422(self):
        resp = client.post("/delete", json={"day": "Monday"}, headers={"user-id": "u1"})
        assert resp.status_code == 422

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.delete_meal", side_effect=HTTPException(400, "user_id required")):
            resp = client.post(
                "/delete",
                json={"day": "Monday", "meal_type": "dinner"},
            )
        assert resp.status_code == 400
