from fastapi import HTTPException

from datetime import (
    date,
    datetime,
    timedelta,
    timezone
)

import uuid
import requests as http_requests

from db.collections import (
    users_collection,
    pending_registrations_collection,
    profiles_collection,
    inventory_collection
)

from dao.inventory_dao import (
    update_inventory,
)


from dao.profile_dao import (
    get_profile,
    update_profile,
)


from services.email_service import (
    send_verification_email
)

from services.shelf_life_service import (
    get_shelf_life,
)

from services.classification_service import (
    classify_item,
)

from services.inventory_maintainance_service import (
    expire_stale_inventory
)


def create_account(data):
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(
            400,
            "Email already registered"
        )

    if users_collection.find_one({"phone": data.phone}):
        raise HTTPException(
            400,
            "Phone number already registered"
        )

    pending_registrations_collection.delete_many(
        {"email": data.email}
    )

    verification_token = str(uuid.uuid4())

    verification_expires = (
        datetime.now(timezone.utc)
        + timedelta(hours=24)
    ).isoformat()

    pending = {
        "_id": str(uuid.uuid4()),
        "email": data.email,
        "password": data.password,
        "name": data.name,
        "phone": data.phone,
        "household_size": data.household_size,
        "diet": data.diet,
        "cooking_frequency": data.cooking_frequency,
        "verification_token": verification_token,
        "verification_token_expires": verification_expires,
        "grocery_shopping_day": data.grocery_shopping_day
    }

    pending_registrations_collection.insert_one(
        pending
    )

    try:
        send_verification_email(
            data.email,
            verification_token
        )

    except Exception as exc:
        pending_registrations_collection.delete_one(
            {"_id": pending["_id"]}
        )

        print(f"[SMTP ERROR] {data.email}: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email. Please try again."
        )

    return {"verification_sent": True}


def login_user(data, background_tasks):
    user = users_collection.find_one({
        "email": data.email,
        "password": data.password
    })

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    if not user.get("verified", True):
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in."
        )

    background_tasks.add_task(
        expire_stale_inventory,
        str(user["_id"])
    )

    profile = profiles_collection.find_one(
        {"user_id": str(user["_id"])},
        {"goals": 1}
    )

    inventory_doc = inventory_collection.find_one(
        {"user_id": str(user["_id"])},
        {"items": 1}
    )

    onboarding_complete = (
        bool(profile and profile.get("goals"))
        and len(
            inventory_doc.get("items", [])
            if inventory_doc else []
        ) >= 5
    )

    return {
        "access_token": str(user["_id"]),
        "user_id": str(user["_id"]),
        "onboarding_complete": onboarding_complete
    }


def verify_email(data):
    pending = pending_registrations_collection.find_one({
        "verification_token": data.token
    })

    if not pending:
        raise HTTPException(
            status_code=404,
            detail="Invalid or already used verification link"
        )

    expires = pending.get(
        "verification_token_expires"
    )

    if expires:
        try:
            expires_at = datetime.fromisoformat(expires)

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )

        if datetime.now(timezone.utc) > expires_at:
            pending_registrations_collection.delete_one(
                {"_id": pending["_id"]}
            )

            raise HTTPException(
                status_code=400,
                detail="Verification link has expired. Please sign up again."
            )

    if users_collection.find_one({
        "email": pending["email"]
    }):
        pending_registrations_collection.delete_one(
            {"_id": pending["_id"]}
        )

        raise HTTPException(
            status_code=400,
            detail="Account already exists. Please log in."
        )

    user_id = str(uuid.uuid4())

    now = datetime.now(timezone.utc)

    user_auth = {
        "_id": user_id,
        "email": pending["email"],
        "password": pending["password"],
        "google_id": None,
        "created_at": now,
        "verified": True,
    }

    user_profile = {
        "user_id": user_id,
        "name": pending["name"],
        "phone": pending.get("phone"),
        "household_size": pending.get("household_size", 1),
        "cooking_frequency": pending.get("cooking_frequency", "daily"),
        "diet": "veg",
        "allergies": [],
        "spice_preference": "medium",
        "goals": [],
        "liked_ingredients": [],
        "disliked_ingredients": [],
        "favorite_cuisines": [],
        "special_preferences": [],
        "grocery_shopping_day": pending.get(
            "grocery_shopping_day",
            "Sunday"
        ),
        "created_at": now,
        "updated_at": now
    }

    user_inventory = {
        "user_id": user_id,
        "items": [],
        "last_restock_week": None,
        "updated_at": now
    }

    users_collection.insert_one(user_auth)

    profiles_collection.insert_one(user_profile)

    inventory_collection.insert_one(user_inventory)

    pending_registrations_collection.delete_one(
        {"_id": pending["_id"]}
    )

    return {
        "user_id": user_id,
        "message": "Email verified. Account created."
    }


def google_auth(data, background_tasks):
    resp = http_requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={data.credential}",
        timeout=10
    )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )

    user_info = resp.json()

    google_id = user_info.get("sub")

    email = user_info.get("email")

    name = user_info.get("name", "")

    if not google_id or not email:
        raise HTTPException(
            status_code=400,
            detail="Missing Google account information"
        )

    user_auth = users_collection.find_one({
        "google_id": google_id
    })

    now = datetime.now(timezone.utc)

    if data.mode == "login":
        if not user_auth:
            raise HTTPException(
                status_code=404,
                detail="No account found. Please sign up first."
            )

        user_id = user_auth["_id"]

    else:
        if user_auth:
            raise HTTPException(
                status_code=400,
                detail="Google account already linked. Please log in."
            )

        user_id = str(uuid.uuid4())

        new_user_auth = {
            "_id": user_id,
            "google_id": google_id,
            "email": email,
            "password": None,
            "verified": True,
            "created_at": now,
        }

        new_user_profile = {
            "user_id": user_id,
            "name": name,
            "phone": None,
            "household_size": data.household_size or 1,
            "cooking_frequency": data.cooking_frequency or "daily",
            "grocery_shopping_day": data.grocery_shopping_day or "Sunday",
            "diet": data.diet or "veg",
            "goals": [],
            "created_at": now,
            "updated_at": now
        }

        new_user_inventory = {
            "user_id": user_id,
            "items": [],
            "updated_at": now
        }

        users_collection.insert_one(new_user_auth)

        profiles_collection.insert_one(new_user_profile)

        inventory_collection.insert_one(new_user_inventory)

    background_tasks.add_task(
        expire_stale_inventory,
        user_id
    )

    profile = profiles_collection.find_one(
        {"user_id": user_id},
        {"goals": 1}
    )

    inventory_doc = inventory_collection.find_one(
        {"user_id": user_id},
        {"items": 1}
    )

    onboarding_complete = (
        bool(profile and profile.get("goals"))
        and len(
            inventory_doc.get("items", [])
            if inventory_doc else []
        ) >= 5
    )

    return {
        "access_token": user_id,
        "user_id": user_id,
        "onboarding_complete": onboarding_complete
    }


def check_verification(email: str):
    user = users_collection.find_one(
        {"email": email},
        {"_id": 1, "verified": 1}
    )

    if user and user.get("verified"):
        return {
            "verified": True,
            "user_id": str(user["_id"])
        }

    return {"verified": False}

def complete_onboarding(
    data,
    background_tasks,
    user_id,
):
    if not user_id:

        raise HTTPException(
            status_code=400,
            detail="user_id header is required"
        )

    profile = get_profile(
        user_id
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    household_size = profile.get(
        "household_size",
        1,
    )

    today = date.today().isoformat()

    now = datetime.now(
        timezone.utc
    )

    inventory_items = []

    for item_name in data.household_items:

        classified = classify_item(
            item_name,
            household_size,
        )

        input_name = item_name.strip().lower()

        resolved_name = classified.get(
            "display_name",
            input_name
        )

        inventory_items.append({

            "display_name":
                resolved_name.title(),

            "aliases":
                [input_name]
                if input_name != resolved_name
                else [],

            "quantity":
                classified.get(
                    "quantity",
                    1
                ),

            "unit":
                classified.get(
                    "unit",
                    "unit"
                ),

            "category":
                classified.get(
                    "category",
                    "Other"
                ),

            "purchase_date":
                today,

            "status":
                "fresh",
        })

    update_profile(
        user_id,

        {
            "goals":
                data.goals,

            "updated_at":
                now,
        }
    )

    update_inventory(
        user_id,

        {
            "items":
                inventory_items,

            "updated_at":
                now,
        }
    )

    for item_name in data.household_items:

        background_tasks.add_task(
            get_shelf_life,
            item_name,
        )

    return {
        "message":
            "Onboarding completed",

        "user_id":
            user_id,
    }