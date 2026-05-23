from db.mongo import db


shelf_life_collection = db[
    "shelf_life"
]

users_collection = db[
    "users"
]

profiles_collection = db[
    "profiles"
]

pending_registrations_collection = db[
    "pending_registrations"
]

inventory_collection = db[
    "inventory"
]

meal_plans_collection = db[
    "meal_plans"
]

nutrition_logs_collection = db[
    "nutrition_logs"
]

chats_collection = db["chats"]

chat_messages_collection = db[
    "chat_messages"
]


recipe_memory_collection = db["recipe_memory"]

agent_events_collection = db["agent_events"]