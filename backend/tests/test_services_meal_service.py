"""Tests for services/meal_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import date, datetime, timezone

_SVC = "services.meal_service"


class TestGetMealPlanService:
    def _today(self):
        return date.today()

    def test_no_user_id_raises_400(self):
        from services.meal_service import get_meal_plan_service
        with pytest.raises(HTTPException) as exc:
            get_meal_plan_service(MagicMock(), None)
        assert exc.value.status_code == 400

    def test_no_meal_doc_returns_empty_meals(self):
        from services.meal_service import get_meal_plan_service
        today = self._today()
        mock_now = MagicMock()
        mock_now.date.return_value = today
        with (
            patch(f"{_SVC}.now_ist", return_value=mock_now),
            patch(f"{_SVC}.get_monday", return_value=today),
            patch(f"{_SVC}.auto_consume_past_meals"),
            patch(f"{_SVC}.run_weekly_restock", return_value=False),
            patch(f"{_SVC}.get_meal_plan", return_value=None),
        ):
            result = get_meal_plan_service(MagicMock(), "u1")
        assert result["meals"] == {}
        assert result["restocked"] is False

    def test_returns_meal_plan(self):
        from services.meal_service import get_meal_plan_service
        today = self._today()
        mock_now = MagicMock()
        mock_now.date.return_value = today
        meals = {"Monday": {"breakfast": [], "lunch": [], "dinner": []}}
        with (
            patch(f"{_SVC}.now_ist", return_value=mock_now),
            patch(f"{_SVC}.get_monday", return_value=today),
            patch(f"{_SVC}.auto_consume_past_meals"),
            patch(f"{_SVC}.run_weekly_restock", return_value=True),
            patch(f"{_SVC}.get_meal_plan", return_value={"meals": meals}),
        ):
            result = get_meal_plan_service(MagicMock(), "u1")
        assert "Monday" in result["meals"]
        assert result["restocked"] is True

    def test_calls_auto_consume(self):
        from services.meal_service import get_meal_plan_service
        today = self._today()
        mock_now = MagicMock()
        mock_now.date.return_value = today
        with (
            patch(f"{_SVC}.now_ist", return_value=mock_now),
            patch(f"{_SVC}.get_monday", return_value=today),
            patch(f"{_SVC}.auto_consume_past_meals") as mock_consume,
            patch(f"{_SVC}.run_weekly_restock", return_value=False),
            patch(f"{_SVC}.get_meal_plan", return_value=None),
        ):
            get_meal_plan_service(MagicMock(), "u1")
        mock_consume.assert_called_once_with("u1", today)


class TestAddMeal:
    def _req(self, day="Monday", meal_type="breakfast", meal_name="Dal"):
        r = MagicMock()
        r.day = day
        r.meal_type = meal_type
        r.meal_name = meal_name
        return r

    def test_no_user_id_raises_400(self):
        from services.meal_service import add_meal
        with pytest.raises(HTTPException) as exc:
            add_meal(self._req(), MagicMock(), None)
        assert exc.value.status_code == 400

    def test_adds_meal_to_plan(self):
        from services.meal_service import add_meal
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        meals = {"Monday": {"breakfast": [], "lunch": [], "dinner": []}}
        meal_doc = {"user_id": "u1", "meals": meals}
        with (
            patch(f"{_SVC}.now_utc", return_value=now),
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.fetch_ingredients", return_value=[{"name": "lentils", "quantity": 100, "unit": "g"}]),
            patch(f"{_SVC}.fuzzy_match", return_value=False),
            patch(f"{_SVC}.get_meal_plan", return_value=meal_doc),
            patch(f"{_SVC}.update_meal_plan") as mock_update,
            patch(f"{_SVC}.store_nutrition_nested"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 2}
            mock_inv.find_one.return_value = {"items": []}
            result = add_meal(self._req(), MagicMock(), "u1")
        assert result["message"] == "Meal added"
        assert "ingredients" in result
        mock_update.assert_called_once()

    def test_invalidates_previous_valid_meal_in_slot(self):
        from services.meal_service import add_meal
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        existing_meal = {"meal_name": "Oatmeal", "valid": True}
        meals = {"Monday": {"breakfast": [existing_meal], "lunch": [], "dinner": []}}
        meal_doc = {"user_id": "u1", "meals": meals}
        with (
            patch(f"{_SVC}.now_utc", return_value=now),
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.fetch_ingredients", return_value=[]),
            patch(f"{_SVC}.fuzzy_match", return_value=False),
            patch(f"{_SVC}.get_meal_plan", return_value=meal_doc),
            patch(f"{_SVC}.update_meal_plan"),
            patch(f"{_SVC}.store_nutrition_nested"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 2}
            mock_inv.find_one.return_value = {"items": []}
            add_meal(self._req(), MagicMock(), "u1")
        assert existing_meal["valid"] is False

    def test_no_meal_doc_creates_new_plan(self):
        from services.meal_service import add_meal
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        with (
            patch(f"{_SVC}.now_utc", return_value=now),
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.fetch_ingredients", return_value=[]),
            patch(f"{_SVC}.fuzzy_match", return_value=False),
            patch(f"{_SVC}.get_meal_plan", return_value=None),
            patch(f"{_SVC}.update_meal_plan") as mock_update,
            patch(f"{_SVC}.store_nutrition_nested"),
        ):
            mock_profiles.find_one.return_value = None
            mock_inv.find_one.return_value = None
            result = add_meal(self._req(), MagicMock(), "u1")
        assert result["message"] == "Meal added"
        mock_update.assert_called_once()


class TestDeleteMeal:
    def _req(self, day="Monday", meal_type="breakfast"):
        r = MagicMock()
        r.day = day
        r.meal_type = meal_type
        return r

    def test_no_user_id_raises_400(self):
        from services.meal_service import delete_meal
        with pytest.raises(HTTPException) as exc:
            delete_meal(self._req(), None)
        assert exc.value.status_code == 400

    def test_no_meal_plan_raises_404(self):
        from services.meal_service import delete_meal
        with patch(f"{_SVC}.get_meal_plan", return_value=None):
            with pytest.raises(HTTPException) as exc:
                delete_meal(self._req(), "u1")
        assert exc.value.status_code == 404

    def test_no_valid_meal_raises_404(self):
        from services.meal_service import delete_meal
        meals = {"Monday": {"breakfast": [{"valid": False, "meal_name": "Dal"}]}}
        with patch(f"{_SVC}.get_meal_plan", return_value={"meals": meals}):
            with pytest.raises(HTTPException) as exc:
                delete_meal(self._req(), "u1")
        assert exc.value.status_code == 404

    def test_deletes_valid_meal(self):
        from services.meal_service import delete_meal
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        meals = {"Monday": {"breakfast": [{"valid": True, "meal_name": "Dal"}]}}
        with (
            patch(f"{_SVC}.get_meal_plan", return_value={"meals": meals}),
            patch(f"{_SVC}.update_meal_plan") as mock_update,
            patch(f"{_SVC}.now_utc", return_value=now),
        ):
            result = delete_meal(self._req(), "u1")
        assert "deleted" in result["message"].lower()
        mock_update.assert_called_once()

    def test_marks_meal_as_skipped(self):
        from services.meal_service import delete_meal
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        meal = {"valid": True, "meal_name": "Dal", "skipped": False}
        meals = {"Monday": {"breakfast": [meal]}}
        with (
            patch(f"{_SVC}.get_meal_plan", return_value={"meals": meals}),
            patch(f"{_SVC}.update_meal_plan"),
            patch(f"{_SVC}.now_utc", return_value=now),
        ):
            delete_meal(self._req(), "u1")
        assert meal["valid"] is False
        assert meal["skipped"] is True
