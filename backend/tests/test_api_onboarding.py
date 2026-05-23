"""API route tests for /onboarding endpoints."""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.routes.onboarding import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

_SVC = "api.routes.onboarding"


class TestCompleteOnboardingRoute:
    def test_success_returns_message_and_user_id(self):
        result = {"message": "Onboarding completed", "user_id": "u1"}
        with patch(f"{_SVC}.complete_onboarding", return_value=result):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": ["Eat healthier"], "household_items": ["rice", "dal"]},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "u1"
        assert "onboarding" in resp.json()["message"].lower()

    def test_no_user_id_returns_400(self):
        with patch(f"{_SVC}.complete_onboarding", side_effect=HTTPException(400, "user_id required")):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": ["Eat healthier"], "household_items": ["rice"]},
            )
        assert resp.status_code == 400

    def test_profile_not_found_returns_404(self):
        with patch(f"{_SVC}.complete_onboarding", side_effect=HTTPException(404, "Profile not found")):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": [], "household_items": []},
                headers={"user-id": "ghost"},
            )
        assert resp.status_code == 404

    def test_missing_required_fields_returns_422(self):
        resp = client.post(
            "/complete-onboarding",
            json={"goals": ["Eat healthier"]},
            headers={"user-id": "u1"},
        )
        assert resp.status_code == 422

    def test_empty_lists_accepted(self):
        result = {"message": "Onboarding completed", "user_id": "u1"}
        with patch(f"{_SVC}.complete_onboarding", return_value=result):
            resp = client.post(
                "/complete-onboarding",
                json={"goals": [], "household_items": []},
                headers={"user-id": "u1"},
            )
        assert resp.status_code == 200
