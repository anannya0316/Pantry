from db.collections import (
    users_collection,
    profiles_collection,
    inventory_collection,
    meal_plans_collection,
    nutrition_logs_collection,
    shelf_life_collection,
    pending_registrations_collection,
    chats_collection,
    chat_messages_collection,
    agent_events_collection,
)


def create_indexes():

    users_collection.create_index(
        "email",
        unique=True
    )

    users_collection.create_index(
        "google_id",
        sparse=True
    )

    profiles_collection.create_index(
        "user_id",
        unique=True
    )

    inventory_collection.create_index(
        "user_id",
        unique=True
    )

    meal_plans_collection.create_index(
        "user_id",
        unique=True
    )

    nutrition_logs_collection.create_index(
        "user_id"
    )

    shelf_life_collection.create_index(
        "item_key",
        unique=True
    )

    pending_registrations_collection.create_index(
        "email"
    )

    pending_registrations_collection.create_index(
        "verification_token"
    )

    chats_collection.create_index(
    [("user_id", 1), ("updated_at", -1)]
    )

    chat_messages_collection.create_index(
        [
            ("chat_id", 1),
            ("created_at", 1)
        ]
    )

    chats_collection.create_index(
    "updated_at",
    expireAfterSeconds=30 * 24 * 3600
    )

    chat_messages_collection.create_index(
    "created_at",
    expireAfterSeconds=30 * 24 * 3600
    )

    agent_events_collection.create_index(
        [("user_id", 1), ("timestamp", -1)]
    )
    agent_events_collection.create_index(
        "timestamp",
        expireAfterSeconds=7 * 24 * 3600,
    )