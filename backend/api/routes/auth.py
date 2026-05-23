from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from models.auth_models import (
    CreateAccountRequest,
    LoginRequest,
    VerifyEmailRequest,
    GoogleAuthRequest
)

from models.onboarding_models import (
    OnboardingRequest
)

from services.auth_service import (
    complete_onboarding,
    create_account,
    login_user,
    verify_email,
    google_auth,
    check_verification
)

from services.onboarding_service import (
    complete_onboarding
)


router = APIRouter()


@router.post("/create-account")
def create_account_route(data: CreateAccountRequest):
    return create_account(data)


@router.post("/login")
def login_route(
    data: LoginRequest,
    background_tasks: BackgroundTasks
):
    return login_user(data, background_tasks)


@router.post("/verify-email")
def verify_email_route(data: VerifyEmailRequest):
    return verify_email(data)


@router.post("/google")
def google_auth_route(
    data: GoogleAuthRequest,
    background_tasks: BackgroundTasks
):
    return google_auth(data, background_tasks)


@router.get("/check-verification")
def check_verification_route(email: str):
    return check_verification(email)


@router.post("/complete-onboarding")
def complete_onboarding_route(
    request: OnboardingRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None),
):
    return complete_onboarding(
        request,
        background_tasks,
        user_id,
    )