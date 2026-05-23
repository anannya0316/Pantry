"""Tests for services/onboarding_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

_SVC = "services.onboarding_service"


class TestCompleteOnboarding:
    def _data(self, goals=None, household_items=None):
        d = MagicMock()
        d.goals = goals or ["Eat healthier"]
        d.household_items = household_items or ["rice", "lentils"]
        return d

    def test_no_user_id_raises_400(self):
        from services.onboarding_service import complete_onboarding
        with pytest.raises(HTTPException) as exc:
            complete_onboarding(self._data(), MagicMock(), None)
        assert exc.value.status_code == 400

    def test_profile_not_found_raises_404(self):
        from services.onboarding_service import complete_onboarding
        with patch(f"{_SVC}.profiles_collection") as mock_profiles:
            mock_profiles.find_one.return_value = None
            with pytest.raises(HTTPException) as exc:
                complete_onboarding(self._data(), MagicMock(), "u1")
        assert exc.value.status_code == 404

    def test_success_returns_message_and_user_id(self):
        from services.onboarding_service import complete_onboarding
        classified = {
            "display_name": "basmati rice",
            "quantity": 2,
            "unit": "kg",
            "category": "Grains",
        }
        with (
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 2}
            result = complete_onboarding(self._data(), MagicMock(), "u1")
        assert result["user_id"] == "u1"
        assert "onboarding" in result["message"].lower()

    def test_updates_profile_and_inventory(self):
        from services.onboarding_service import complete_onboarding
        classified = {"display_name": "rice", "quantity": 1, "unit": "kg", "category": "Grains"}
        with (
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 2}
            complete_onboarding(self._data(), MagicMock(), "u1")
        mock_profiles.update_one.assert_called_once()
        mock_inv.update_one.assert_called_once()

    def test_schedules_shelf_life_task_for_each_item(self):
        from services.onboarding_service import complete_onboarding
        bt = MagicMock()
        items = ["rice", "lentils", "oil"]
        classified = {"display_name": "rice", "quantity": 1, "unit": "kg", "category": "Grains"}
        with (
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection"),
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 1}
            complete_onboarding(self._data(household_items=items), bt, "u1")
        assert bt.add_task.call_count == len(items)

    def test_title_cases_display_name(self):
        from services.onboarding_service import complete_onboarding
        classified = {"display_name": "basmati rice", "quantity": 1, "unit": "kg", "category": "Grains"}
        captured = []

        def fake_inv_update(query, update):
            captured.append(update)

        with (
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            mock_profiles.find_one.return_value = {"household_size": 2}
            mock_inv.update_one.side_effect = fake_inv_update
            complete_onboarding(self._data(household_items=["basmati rice"]), MagicMock(), "u1")

        items_saved = captured[0]["$set"]["items"]
        assert items_saved[0]["display_name"] == "Basmati Rice"
