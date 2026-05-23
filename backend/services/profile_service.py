from fastapi import HTTPException

from dao.profile_dao import (
    get_profile,
    update_profile,
    get_auth_user
)


def get_user_profile(
    user_id: str
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    profile = get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    auth = get_auth_user(user_id)

    if auth:
        profile["email"] = auth.get(
            "email"
        )

    profile["_id"] = str(
        profile["_id"]
    )

    return profile


def update_user_goals(
    request,
    user_id: str
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    result = update_profile(
        user_id,
        {
            "goals": request.goals
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "Goals updated successfully",
        "goals": request.goals
    }


def update_user_profile(
    request,
    user_id: str
):
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    updates = {
        key: value
        for key, value
        in request.model_dump().items()
        if value is not None
    }

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )

    result = update_profile(
        user_id,
        updates
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return {
        "message": "Profile updated successfully"
    }