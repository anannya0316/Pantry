from db.collections import (
    users_collection,
    profiles_collection,
    pending_registrations_collection,
    inventory_collection,
    meal_plans_collection,
    nutrition_logs_collection,
    shelf_life_collection,
    chats_collection,
    chat_messages_collection,
)


def reset_database():

    users_collection.delete_many({})

    profiles_collection.delete_many({})

    pending_registrations_collection.delete_many({})

    inventory_collection.delete_many({})

    meal_plans_collection.delete_many({})

    nutrition_logs_collection.delete_many({})

    shelf_life_collection.delete_many({})

    chats_collection.delete_many({})

    chat_messages_collection.delete_many({})

    print(
        "Database reset complete."
    )


if __name__ == "__main__":

    confirm = input(
        "Delete ALL database data? "
        "(yes/no): "
    )

    if confirm.lower() == "yes":

        reset_database()

    else:

        print("Cancelled.")