"""Tests for services/auth_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta

_SVC = "services.auth_service"


class TestCreateAccount:
    def _req(self, email="new@test.com", phone="1234567890"):
        r = MagicMock()
        r.email = email
        r.phone = phone
        r.password = "password1"
        r.name = "Alice"
        r.household_size = 2
        r.diet = "veg"
        r.cooking_frequency = "daily"
        r.grocery_shopping_day = "Sunday"
        return r

    def test_duplicate_email_raises_400(self):
        from services.auth_service import create_account
        req = self._req()
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = {"email": req.email}
            with pytest.raises(HTTPException) as exc:
                create_account(req)
        assert exc.value.status_code == 400
        assert "Email" in exc.value.detail

    def test_duplicate_phone_raises_400(self):
        from services.auth_service import create_account
        req = self._req()
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.side_effect = [None, {"phone": req.phone}]
            with pytest.raises(HTTPException) as exc:
                create_account(req)
        assert exc.value.status_code == 400
        assert "Phone" in exc.value.detail

    def test_email_send_failure_raises_500_and_rolls_back(self):
        from services.auth_service import create_account
        req = self._req()
        with (
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.pending_registrations_collection") as mock_pending,
            patch(f"{_SVC}.send_verification_email", side_effect=Exception("SMTP error")),
        ):
            mock_users.find_one.return_value = None
            with pytest.raises(HTTPException) as exc:
                create_account(req)
        assert exc.value.status_code == 500
        mock_pending.delete_one.assert_called_once()

    def test_success_returns_verification_sent(self):
        from services.auth_service import create_account
        req = self._req()
        with (
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.pending_registrations_collection"),
            patch(f"{_SVC}.send_verification_email"),
        ):
            mock_users.find_one.return_value = None
            result = create_account(req)
        assert result["verification_sent"] is True


class TestLoginUser:
    def _req(self, email="a@test.com", password="pass"):
        r = MagicMock()
        r.email = email
        r.password = password
        return r

    def test_invalid_credentials_raises_400(self):
        from services.auth_service import login_user
        req = self._req()
        bt = MagicMock()
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = None
            with pytest.raises(HTTPException) as exc:
                login_user(req, bt)
        assert exc.value.status_code == 400

    def test_unverified_user_raises_403(self):
        from services.auth_service import login_user
        req = self._req()
        bt = MagicMock()
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = {"_id": "uid1", "verified": False}
            with pytest.raises(HTTPException) as exc:
                login_user(req, bt)
        assert exc.value.status_code == 403

    def test_login_success_with_onboarding_complete(self):
        from services.auth_service import login_user
        req = self._req()
        bt = MagicMock()
        with (
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.expire_stale_inventory"),
        ):
            mock_users.find_one.return_value = {"_id": "uid1", "verified": True}
            mock_profiles.find_one.return_value = {"goals": ["Eat healthier"]}
            mock_inv.find_one.return_value = {"items": [{}] * 5}
            result = login_user(req, bt)
        assert result["user_id"] == "uid1"
        assert result["onboarding_complete"] is True

    def test_login_success_onboarding_incomplete(self):
        from services.auth_service import login_user
        req = self._req()
        bt = MagicMock()
        with (
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.expire_stale_inventory"),
        ):
            mock_users.find_one.return_value = {"_id": "uid1", "verified": True}
            mock_profiles.find_one.return_value = {"goals": []}
            mock_inv.find_one.return_value = {"items": []}
            result = login_user(req, bt)
        assert result["onboarding_complete"] is False

    def test_schedules_expire_stale_inventory(self):
        from services.auth_service import login_user
        req = self._req()
        bt = MagicMock()
        with (
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.expire_stale_inventory") as mock_expire,
        ):
            mock_users.find_one.return_value = {"_id": "uid1", "verified": True}
            mock_profiles.find_one.return_value = None
            mock_inv.find_one.return_value = None
            login_user(req, bt)
        bt.add_task.assert_called_once_with(mock_expire, "uid1")


class TestVerifyEmail:
    def _req(self, token="tok123"):
        r = MagicMock()
        r.token = token
        return r

    def _future(self, hours=23):
        return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()

    def test_invalid_token_raises_404(self):
        from services.auth_service import verify_email
        req = self._req()
        with patch(f"{_SVC}.pending_registrations_collection") as mock_pend:
            mock_pend.find_one.return_value = None
            with pytest.raises(HTTPException) as exc:
                verify_email(req)
        assert exc.value.status_code == 404

    def test_expired_token_raises_400(self):
        from services.auth_service import verify_email
        req = self._req()
        expired = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        with patch(f"{_SVC}.pending_registrations_collection") as mock_pend:
            mock_pend.find_one.return_value = {
                "_id": "pid1",
                "email": "a@test.com",
                "verification_token_expires": expired,
            }
            with pytest.raises(HTTPException) as exc:
                verify_email(req)
        assert exc.value.status_code == 400
        assert "expired" in exc.value.detail.lower()

    def test_invalid_isoformat_raises_400(self):
        from services.auth_service import verify_email
        req = self._req()
        with patch(f"{_SVC}.pending_registrations_collection") as mock_pend:
            mock_pend.find_one.return_value = {
                "_id": "pid1",
                "email": "a@test.com",
                "verification_token_expires": "not-a-date",
            }
            with pytest.raises(HTTPException) as exc:
                verify_email(req)
        assert exc.value.status_code == 400

    def test_account_already_exists_raises_400(self):
        from services.auth_service import verify_email
        req = self._req()
        with (
            patch(f"{_SVC}.pending_registrations_collection") as mock_pend,
            patch(f"{_SVC}.users_collection") as mock_users,
        ):
            mock_pend.find_one.return_value = {
                "_id": "pid1",
                "email": "a@test.com",
                "verification_token_expires": self._future(),
            }
            mock_users.find_one.return_value = {"email": "a@test.com"}
            with pytest.raises(HTTPException) as exc:
                verify_email(req)
        assert exc.value.status_code == 400
        assert "already exists" in exc.value.detail.lower()

    def test_success_creates_user_profile_inventory(self):
        from services.auth_service import verify_email
        req = self._req()
        pending = {
            "_id": "pid1",
            "email": "a@test.com",
            "password": "hashed",
            "name": "Alice",
            "phone": "123",
            "household_size": 2,
            "cooking_frequency": "daily",
            "verification_token_expires": self._future(),
        }
        with (
            patch(f"{_SVC}.pending_registrations_collection") as mock_pend,
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
        ):
            mock_pend.find_one.return_value = pending
            mock_users.find_one.return_value = None
            result = verify_email(req)
        assert "user_id" in result
        mock_users.insert_one.assert_called_once()
        mock_profiles.insert_one.assert_called_once()
        mock_inv.insert_one.assert_called_once()
        mock_pend.delete_one.assert_called_once()


class TestGoogleAuth:
    def _req(self, mode="login", **kwargs):
        r = MagicMock()
        r.credential = "gtoken"
        r.mode = mode
        r.household_size = kwargs.get("household_size", 2)
        r.cooking_frequency = kwargs.get("cooking_frequency", "daily")
        r.grocery_shopping_day = kwargs.get("grocery_shopping_day", "Sunday")
        r.diet = kwargs.get("diet", "veg")
        return r

    def _google_resp(self, status=200, sub="gsub123", email="g@test.com", name="Goog"):
        resp = MagicMock()
        resp.status_code = status
        resp.json.return_value = {"sub": sub, "email": email, "name": name}
        return resp

    def test_invalid_google_token_raises_401(self):
        from services.auth_service import google_auth
        req = self._req()
        bt = MagicMock()
        with patch(f"{_SVC}.http_requests") as mock_http:
            mock_http.get.return_value = self._google_resp(status=400)
            with pytest.raises(HTTPException) as exc:
                google_auth(req, bt)
        assert exc.value.status_code == 401

    def test_login_mode_user_not_found_raises_404(self):
        from services.auth_service import google_auth
        req = self._req(mode="login")
        bt = MagicMock()
        with (
            patch(f"{_SVC}.http_requests") as mock_http,
            patch(f"{_SVC}.users_collection") as mock_users,
        ):
            mock_http.get.return_value = self._google_resp()
            mock_users.find_one.return_value = None
            with pytest.raises(HTTPException) as exc:
                google_auth(req, bt)
        assert exc.value.status_code == 404

    def test_signup_mode_existing_account_raises_400(self):
        from services.auth_service import google_auth
        req = self._req(mode="signup")
        bt = MagicMock()
        with (
            patch(f"{_SVC}.http_requests") as mock_http,
            patch(f"{_SVC}.users_collection") as mock_users,
        ):
            mock_http.get.return_value = self._google_resp()
            mock_users.find_one.return_value = {"google_id": "gsub123"}
            with pytest.raises(HTTPException) as exc:
                google_auth(req, bt)
        assert exc.value.status_code == 400

    def test_login_mode_success_returns_user_id(self):
        from services.auth_service import google_auth
        req = self._req(mode="login")
        bt = MagicMock()
        with (
            patch(f"{_SVC}.http_requests") as mock_http,
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.expire_stale_inventory"),
        ):
            mock_http.get.return_value = self._google_resp()
            mock_users.find_one.return_value = {"_id": "uid1", "google_id": "gsub123"}
            mock_profiles.find_one.return_value = {"goals": ["Lose weight"]}
            mock_inv.find_one.return_value = {"items": [{}] * 6}
            result = google_auth(req, bt)
        assert result["user_id"] == "uid1"
        assert result["onboarding_complete"] is True

    def test_signup_mode_creates_records(self):
        from services.auth_service import google_auth
        req = self._req(mode="signup")
        bt = MagicMock()
        with (
            patch(f"{_SVC}.http_requests") as mock_http,
            patch(f"{_SVC}.users_collection") as mock_users,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.expire_stale_inventory"),
        ):
            mock_http.get.return_value = self._google_resp()
            mock_users.find_one.return_value = None
            mock_profiles.find_one.return_value = None
            mock_inv.find_one.return_value = None
            result = google_auth(req, bt)
        assert "user_id" in result
        mock_users.insert_one.assert_called_once()
        mock_profiles.insert_one.assert_called_once()
        mock_inv.insert_one.assert_called_once()


class TestCheckVerification:
    def test_verified_user_returns_true_with_user_id(self):
        from services.auth_service import check_verification
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = {"_id": "uid1", "verified": True}
            result = check_verification("a@test.com")
        assert result["verified"] is True
        assert result["user_id"] == "uid1"

    def test_unverified_user_returns_false(self):
        from services.auth_service import check_verification
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = {"_id": "uid1", "verified": False}
            result = check_verification("a@test.com")
        assert result["verified"] is False

    def test_user_not_found_returns_false(self):
        from services.auth_service import check_verification
        with patch(f"{_SVC}.users_collection") as mock_users:
            mock_users.find_one.return_value = None
            result = check_verification("ghost@test.com")
        assert result["verified"] is False


class TestCompleteOnboardingAuthService:
    def _data(self, goals=None, household_items=None):
        d = MagicMock()
        d.goals = goals or ["Eat healthier"]
        d.household_items = household_items or ["rice", "lentils"]
        return d

    def test_no_user_id_raises_400(self):
        from services.auth_service import complete_onboarding
        with pytest.raises(HTTPException) as exc:
            complete_onboarding(self._data(), MagicMock(), None)
        assert exc.value.status_code == 400

    def test_profile_not_found_raises_404(self):
        from services.auth_service import complete_onboarding
        with patch(f"{_SVC}.get_profile", return_value=None):
            with pytest.raises(HTTPException) as exc:
                complete_onboarding(self._data(), MagicMock(), "u1")
        assert exc.value.status_code == 404

    def test_success_updates_profile_and_inventory(self):
        from services.auth_service import complete_onboarding
        classified = {
            "display_name": "basmati rice",
            "quantity": 2,
            "unit": "kg",
            "category": "Grains",
        }
        with (
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2}),
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.update_profile") as mock_update_profile,
            patch(f"{_SVC}.update_inventory") as mock_update_inv,
            patch(f"{_SVC}.get_shelf_life"),
        ):
            result = complete_onboarding(self._data(), MagicMock(), "u1")
        assert result["user_id"] == "u1"
        assert "onboarding" in result["message"].lower()
        mock_update_profile.assert_called_once()
        mock_update_inv.assert_called_once()

    def test_schedules_shelf_life_for_each_item(self):
        from services.auth_service import complete_onboarding
        bt = MagicMock()
        items = ["rice", "lentils", "oil"]
        classified = {"display_name": "rice", "quantity": 1, "unit": "kg", "category": "Grains"}
        with (
            patch(f"{_SVC}.get_profile", return_value={"household_size": 2}),
            patch(f"{_SVC}.classify_item", return_value=classified),
            patch(f"{_SVC}.update_profile"),
            patch(f"{_SVC}.update_inventory"),
            patch(f"{_SVC}.get_shelf_life"),
        ):
            complete_onboarding(self._data(household_items=items), bt, "u1")
        assert bt.add_task.call_count == len(items)
