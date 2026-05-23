"""API route tests for /nutrition endpoints."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from api.routes.nutrition import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.nutrition"


class TestLogRecipeRoute:
    def test_no_user_id_returns_400(self):
        resp = client.post("/log-recipe", json={"meal_name": "Pasta"})
        assert resp.status_code == 400

    def test_returns_meal_logged(self):
        with patch(f"{_SVC}.log_recipe_background"):
            resp = client.post(
                "/log-recipe",
                json={"meal_name": "Pasta", "meal_type": "lunch"},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Meal logged"

    def test_meal_type_inferred_when_missing(self):
        """Route should infer meal_type from current IST hour when not provided."""
        with (
            patch(f"{_SVC}.now_ist") as mock_now,
            patch(f"{_SVC}.log_recipe_background"),
        ):
            mock_now.return_value.hour = 8  # 8am → breakfast
            resp = client.post(
                "/log-recipe",
                json={"meal_name": "Oatmeal"},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200

    def test_breakfast_inferred_before_10(self):
        captured_meal_type = []
        def capture(user_id, meal_name, meal_type):
            captured_meal_type.append(meal_type)
        with (
            patch(f"{_SVC}.now_ist") as mock_now,
            patch(f"{_SVC}.log_recipe_background", side_effect=capture),
        ):
            mock_now.return_value.hour = 8
            client.post("/log-recipe", json={"meal_name": "Eggs"}, headers={"user-id": "u1"})
        assert captured_meal_type[0] == "breakfast"

    def test_lunch_inferred_between_10_and_15(self):
        captured = []
        def capture(user_id, meal_name, meal_type):
            captured.append(meal_type)
        with (
            patch(f"{_SVC}.now_ist") as mock_now,
            patch(f"{_SVC}.log_recipe_background", side_effect=capture),
        ):
            mock_now.return_value.hour = 12
            client.post("/log-recipe", json={"meal_name": "Rice"}, headers={"user-id": "u1"})
        assert captured[0] == "lunch"

    def test_dinner_inferred_after_15(self):
        captured = []
        def capture(user_id, meal_name, meal_type):
            captured.append(meal_type)
        with (
            patch(f"{_SVC}.now_ist") as mock_now,
            patch(f"{_SVC}.log_recipe_background", side_effect=capture),
        ):
            mock_now.return_value.hour = 19
            client.post("/log-recipe", json={"meal_name": "Dal"}, headers={"user-id": "u1"})
        assert captured[0] == "dinner"


class TestNutritionInsightsRoute:
    def test_returns_insights(self):
        insights = {
            "streak": 3, "avg_calories": 1800, "meals_logged": 9,
            "health_score": 72, "weekly_trend": [], "today_macros": {},
            "macro_distribution": {}, "nutrient_goals": [],
            "nutrition_goals_pct": 80, "nutrition_goals_sub": "...",
            "meal_consistency": "Good", "meal_consistency_sub": "...",
            "diet_balance_pct": 65, "period": "weekly"
        }
        with patch(f"{_SVC}.get_nutrition_insights", return_value=insights):
            resp = client.get("/insights", headers={"user-id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["streak"] == 3

    def test_period_parameter_passed_to_service(self):
        captured = []
        def capture(user_id, period="weekly"):
            captured.append(period)
            return {}
        with patch(f"{_SVC}.get_nutrition_insights", side_effect=capture):
            client.get("/insights?period=monthly", headers={"user-id": "u1"})
        assert captured[0] == "monthly"

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.get_nutrition_insights", side_effect=HTTPException(400, "user_id required")):
            resp = client.get("/insights")
        assert resp.status_code == 400
