"""API route tests for /auth endpoints."""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.routes.auth import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.auth"

_VALID_CREATE = {
    "email": "alice@test.com",
    "password": "password1",
    "name": "Alice",
    "phone": "1234567890",
    "household_size": 2,
    "diet": "veg",
    "cooking_frequency": "daily",
    "grocery_shopping_day": "Sunday",
}


class TestCreateAccountRoute:
    def test_success_returns_verification_sent(self):
        with patch(f"{_SVC}.create_account", return_value={"verification_sent": True}):
            resp = client.post("/create-account", json=_VALID_CREATE)
        assert resp.status_code == 200
        assert resp.json()["verification_sent"] is True

    def test_duplicate_email_returns_400(self):
        with patch(f"{_SVC}.create_account", side_effect=HTTPException(400, "Email already registered")):
            resp = client.post("/create-account", json=_VALID_CREATE)
        assert resp.status_code == 400

    def test_missing_required_field_returns_422(self):
        body = {k: v for k, v in _VALID_CREATE.items() if k != "email"}
        resp = client.post("/create-account", json=body)
        assert resp.status_code == 422


class TestLoginRoute:
    def test_success_returns_access_token(self):
        result = {"access_token": "uid1", "user_id": "uid1", "onboarding_complete": True}
        with patch(f"{_SVC}.login_user", return_value=result):
            resp = client.post("/login", json={"email": "a@test.com", "password": "pass"})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "uid1"

    def test_invalid_credentials_returns_400(self):
        with patch(f"{_SVC}.login_user", side_effect=HTTPException(400, "Invalid credentials")):
            resp = client.post("/login", json={"email": "a@test.com", "password": "wrong"})
        assert resp.status_code == 400

    def test_unverified_user_returns_403(self):
        with patch(f"{_SVC}.login_user", side_effect=HTTPException(403, "Verify email")):
            resp = client.post("/login", json={"email": "a@test.com", "password": "pass"})
        assert resp.status_code == 403


class TestVerifyEmailRoute:
    def test_success_creates_account(self):
        result = {"user_id": "uid1", "message": "Email verified. Account created."}
        with patch(f"{_SVC}.verify_email", return_value=result):
            resp = client.post("/verify-email", json={"token": "tok123"})
        assert resp.status_code == 200
        assert "user_id" in resp.json()

    def test_invalid_token_returns_404(self):
        with patch(f"{_SVC}.verify_email", side_effect=HTTPException(404, "Invalid token")):
            resp = client.post("/verify-email", json={"token": "badtoken"})
        assert resp.status_code == 404

    def test_expired_token_returns_400(self):
        with patch(f"{_SVC}.verify_email", side_effect=HTTPException(400, "Verification link has expired")):
            resp = client.post("/verify-email", json={"token": "oldtoken"})
        assert resp.status_code == 400


class TestGoogleAuthRoute:
    def test_success_returns_user_id(self):
        result = {"access_token": "uid1", "user_id": "uid1", "onboarding_complete": False}
        with patch(f"{_SVC}.google_auth", return_value=result):
            resp = client.post("/google", json={"credential": "gtoken", "mode": "login"})
        assert resp.status_code == 200
        assert "user_id" in resp.json()

    def test_invalid_token_returns_401(self):
        with patch(f"{_SVC}.google_auth", side_effect=HTTPException(401, "Invalid Google token")):
            resp = client.post("/google", json={"credential": "bad", "mode": "login"})
        assert resp.status_code == 401

    def test_account_not_found_returns_404(self):
        with patch(f"{_SVC}.google_auth", side_effect=HTTPException(404, "No account found")):
            resp = client.post("/google", json={"credential": "gtoken", "mode": "login"})
        assert resp.status_code == 404


class TestCheckVerificationRoute:
    def test_verified_user_returns_true(self):
        with patch(f"{_SVC}.check_verification", return_value={"verified": True, "user_id": "uid1"}):
            resp = client.get("/check-verification", params={"email": "a@test.com"})
        assert resp.status_code == 200
        assert resp.json()["verified"] is True

    def test_unverified_user_returns_false(self):
        with patch(f"{_SVC}.check_verification", return_value={"verified": False}):
            resp = client.get("/check-verification", params={"email": "pending@test.com"})
        assert resp.status_code == 200
        assert resp.json()["verified"] is False


class TestCompleteOnboardingRoute:
    def test_success(self):
        result = {"message": "Onboarding completed", "user_id": "u1"}
        with patch(f"{_SVC}.complete_onboarding", return_value=result):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": ["Eat healthier"], "household_items": ["rice"]},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
        assert "onboarding" in resp.json()["message"].lower()

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.complete_onboarding", side_effect=HTTPException(400, "user_id required")):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": ["Eat healthier"], "household_items": ["rice"]},
            )
        assert resp.status_code == 400
