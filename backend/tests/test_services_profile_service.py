"""Tests for services/profile_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

_SVC = "services.profile_service"


def _mock_update(matched=1):
    r = MagicMock()
    r.matched_count = matched
    return r


class TestGetUserProfile:
    def test_no_user_id_raises_400(self):
        from services.profile_service import get_user_profile
        with pytest.raises(HTTPException) as exc:
            get_user_profile(None)
        assert exc.value.status_code == 400

    def test_profile_not_found_raises_404(self):
        from services.profile_service import get_user_profile
        with (
            patch(f"{_SVC}.get_profile", return_value=None),
            patch(f"{_SVC}.get_auth_user", return_value=None),
        ):
            with pytest.raises(HTTPException) as exc:
                get_user_profile("u1")
        assert exc.value.status_code == 404

    def test_returns_profile_with_email_from_auth(self):
        from services.profile_service import get_user_profile
        profile = {"_id": "abc", "user_id": "u1", "name": "Alice"}
        with (
            patch(f"{_SVC}.get_profile", return_value=profile),
            patch(f"{_SVC}.get_auth_user", return_value={"email": "alice@test.com"}),
        ):
            result = get_user_profile("u1")
        assert result["email"] == "alice@test.com"
        assert isinstance(result["_id"], str)

    def test_no_auth_user_still_returns_profile(self):
        from services.profile_service import get_user_profile
        profile = {"_id": "abc", "user_id": "u1", "name": "Bob"}
        with (
            patch(f"{_SVC}.get_profile", return_value=profile),
            patch(f"{_SVC}.get_auth_user", return_value=None),
        ):
            result = get_user_profile("u1")
        assert result["name"] == "Bob"
        assert "email" not in result


class TestUpdateUserGoals:
    def test_no_user_id_raises_400(self):
        from services.profile_service import update_user_goals
        req = MagicMock(goals=["Eat healthier"])
        with pytest.raises(HTTPException) as exc:
            update_user_goals(req, None)
        assert exc.value.status_code == 400

    def test_user_not_found_raises_404(self):
        from services.profile_service import update_user_goals
        req = MagicMock(goals=["Eat healthier"])
        with patch(f"{_SVC}.update_profile", return_value=_mock_update(matched=0)):
            with pytest.raises(HTTPException) as exc:
                update_user_goals(req, "u1")
        assert exc.value.status_code == 404

    def test_success_returns_goals(self):
        from services.profile_service import update_user_goals
        req = MagicMock(goals=["Gain muscle", "Eat healthier"])
        with patch(f"{_SVC}.update_profile", return_value=_mock_update()):
            result = update_user_goals(req, "u1")
        assert result["goals"] == ["Gain muscle", "Eat healthier"]
        assert "updated" in result["message"].lower()


class TestUpdateUserProfile:
    def test_no_user_id_raises_400(self):
        from services.profile_service import update_user_profile
        req = MagicMock()
        req.model_dump.return_value = {"household_size": 3}
        with pytest.raises(HTTPException) as exc:
            update_user_profile(req, None)
        assert exc.value.status_code == 400

    def test_no_fields_to_update_raises_400(self):
        from services.profile_service import update_user_profile
        req = MagicMock()
        req.model_dump.return_value = {"household_size": None, "diet": None}
        with pytest.raises(HTTPException) as exc:
            update_user_profile(req, "u1")
        assert exc.value.status_code == 400

    def test_profile_not_found_raises_404(self):
        from services.profile_service import update_user_profile
        req = MagicMock()
        req.model_dump.return_value = {"household_size": 3}
        with patch(f"{_SVC}.update_profile", return_value=_mock_update(matched=0)):
            with pytest.raises(HTTPException) as exc:
                update_user_profile(req, "u1")
        assert exc.value.status_code == 404

    def test_success_returns_message(self):
        from services.profile_service import update_user_profile
        req = MagicMock()
        req.model_dump.return_value = {"household_size": 4, "diet": None}
        with patch(f"{_SVC}.update_profile", return_value=_mock_update()):
            result = update_user_profile(req, "u1")
        assert "updated" in result["message"].lower()
