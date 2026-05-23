"""Tests for chatbot/tools/profile.py."""
import pytest
from unittest.mock import patch, MagicMock

_MOD = "chatbot.tools.profile"


class TestGetProfile:
    def test_no_user_id_returns_failure(self):
        from chatbot.tools.profile import get_profile
        result = get_profile("")
        assert result["success"] is False
        assert "user_id" in result["error"]

    def test_profile_not_found_returns_failure(self):
        from chatbot.tools.profile import get_profile
        with (
            patch(f"{_MOD}._get_profile_dao", return_value=None),
            patch(f"{_MOD}.get_auth_user", return_value=None),
        ):
            result = get_profile("u1")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_returns_profile_with_email(self):
        from chatbot.tools.profile import get_profile
        profile = {"user_id": "u1", "name": "Alice", "_id": "abc123"}
        auth = {"email": "alice@example.com"}
        with (
            patch(f"{_MOD}._get_profile_dao", return_value=profile),
            patch(f"{_MOD}.get_auth_user", return_value=auth),
        ):
            result = get_profile("u1")
        assert result["success"] is True
        assert result["profile"]["email"] == "alice@example.com"

    def test_id_stringified(self):
        from chatbot.tools.profile import get_profile
        profile = {"user_id": "u1", "_id": "raw_object_id"}
        with (
            patch(f"{_MOD}._get_profile_dao", return_value=profile),
            patch(f"{_MOD}.get_auth_user", return_value=None),
        ):
            result = get_profile("u1")
        assert isinstance(result["profile"]["_id"], str)

    def test_exception_returns_failure(self):
        from chatbot.tools.profile import get_profile
        with patch(f"{_MOD}._get_profile_dao", side_effect=RuntimeError("DB error")):
            result = get_profile("u1")
        assert result["success"] is False
        assert "Unexpected error" in result["error"]


class TestUpdateProfile:
    def _mock_result(self, matched=1):
        r = MagicMock()
        r.matched_count = matched
        return r

    def test_no_user_id_returns_failure(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("")
        assert result["success"] is False

    def test_no_updates_provided_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1")
        assert result["success"] is False
        assert "No fields" in result["error"]

    def test_invalid_diet_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", diet="pescatarian")
        assert result["success"] is False
        assert "Invalid diet" in result["error"]

    def test_invalid_shopping_day_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", grocery_shopping_day="Someday")
        assert result["success"] is False
        assert "Invalid grocery_shopping_day" in result["error"]

    def test_invalid_goal_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", goals=["Become immortal"])
        assert result["success"] is False
        assert "Invalid goals" in result["error"]

    def test_goals_not_list_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", goals="Eat healthier")
        assert result["success"] is False

    def test_household_size_zero_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", household_size=0)
        assert result["success"] is False

    def test_household_size_negative_fails(self):
        from chatbot.tools.profile import update_profile
        result = update_profile("u1", household_size=-1)
        assert result["success"] is False

    def test_profile_not_found_fails(self):
        from chatbot.tools.profile import update_profile
        with patch(f"{_MOD}._update_profile_dao", return_value=self._mock_result(matched=0)):
            result = update_profile("u1", household_size=3)
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_successful_update(self):
        from chatbot.tools.profile import update_profile
        with patch(f"{_MOD}._update_profile_dao", return_value=self._mock_result(matched=1)):
            result = update_profile("u1", household_size=4)
        assert result["success"] is True
        assert "household_size" in result["updated_fields"]

    def test_valid_diet_succeeds(self):
        from chatbot.tools.profile import update_profile
        with patch(f"{_MOD}._update_profile_dao", return_value=self._mock_result()):
            result = update_profile("u1", diet="veg")
        assert result["success"] is True

    def test_valid_goals_succeed(self):
        from chatbot.tools.profile import update_profile
        with patch(f"{_MOD}._update_profile_dao", return_value=self._mock_result()):
            result = update_profile("u1", goals=["Eat healthier", "Lose weight"])
        assert result["success"] is True

    def test_exception_returns_failure(self):
        from chatbot.tools.profile import update_profile
        with patch(f"{_MOD}._update_profile_dao", side_effect=RuntimeError("timeout")):
            result = update_profile("u1", household_size=2)
        assert result["success"] is False
