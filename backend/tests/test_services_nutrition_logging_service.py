"""Tests for services/nutrition_logging_service.py."""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timezone

_SVC = "services.nutrition_logging_service"


class TestLogRecipeBackground:
    def test_logs_nutrition_with_health_score(self):
        from services.nutrition_logging_service import log_recipe_background
        nutrition = {"calories": 500, "protein": 30}
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        with (
            patch(f"{_SVC}.fetch_nutrition", return_value=nutrition),
            patch(f"{_SVC}.now_utc", return_value=now),
            patch(f"{_SVC}.get_profile", return_value={"goals": ["Lose weight"]}),
            patch(f"{_SVC}.get_daily_targets", return_value={"calories": 2000}) as mock_targets,
            patch(f"{_SVC}.calculate_meal_health_score", return_value=75) as mock_score,
            patch(f"{_SVC}.insert_nutrition_log") as mock_insert,
        ):
            log_recipe_background("u1", "Grilled Chicken", "lunch")

        mock_targets.assert_called_once_with(["Lose weight"])
        mock_score.assert_called_once()
        log_call = mock_insert.call_args[0][0]
        assert log_call["user_id"] == "u1"
        assert log_call["meal"] == "Grilled Chicken"
        assert log_call["meal_type"] == "lunch"
        assert log_call["health_score"] == 75
        assert log_call["nutrition"] == nutrition
        assert log_call["created_at"] == now

    def test_no_user_profile_uses_empty_goals(self):
        from services.nutrition_logging_service import log_recipe_background
        with (
            patch(f"{_SVC}.fetch_nutrition", return_value={}),
            patch(f"{_SVC}.now_utc", return_value=datetime(2024, 1, 1, tzinfo=timezone.utc)),
            patch(f"{_SVC}.get_profile", return_value=None),
            patch(f"{_SVC}.get_daily_targets", return_value={}) as mock_targets,
            patch(f"{_SVC}.calculate_meal_health_score", return_value=50),
            patch(f"{_SVC}.insert_nutrition_log"),
        ):
            log_recipe_background("u1", "Dal", "dinner")

        mock_targets.assert_called_once_with([])

    def test_passes_correct_args_to_health_score(self):
        from services.nutrition_logging_service import log_recipe_background
        nutrition = {"calories": 400}
        now = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
        targets = {"calories": 1800}
        with (
            patch(f"{_SVC}.fetch_nutrition", return_value=nutrition),
            patch(f"{_SVC}.now_utc", return_value=now),
            patch(f"{_SVC}.get_profile", return_value={"goals": ["Build muscle"]}),
            patch(f"{_SVC}.get_daily_targets", return_value=targets),
            patch(f"{_SVC}.calculate_meal_health_score", return_value=80) as mock_score,
            patch(f"{_SVC}.insert_nutrition_log"),
        ):
            log_recipe_background("u1", "Protein Shake", "breakfast")

        mock_score.assert_called_once_with(
            meal_name="Protein Shake",
            nutrition=nutrition,
            meal_type="breakfast",
            created_at=now,
            daily_targets=targets,
        )

    def test_insert_is_always_called(self):
        from services.nutrition_logging_service import log_recipe_background
        with (
            patch(f"{_SVC}.fetch_nutrition", return_value={}),
            patch(f"{_SVC}.now_utc", return_value=datetime(2024, 1, 1, tzinfo=timezone.utc)),
            patch(f"{_SVC}.get_profile", return_value=None),
            patch(f"{_SVC}.get_daily_targets", return_value={}),
            patch(f"{_SVC}.calculate_meal_health_score", return_value=0),
            patch(f"{_SVC}.insert_nutrition_log") as mock_insert,
        ):
            log_recipe_background("u2", "Toast", "breakfast")

        mock_insert.assert_called_once()
