import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import settings  # loads .env
from services.ingredient_service import fetch_ingredients

meals = ["fried rice"]

for meal in meals:
    print(f"\n--- {meal} ---")
    result = fetch_ingredients(
        meal_name=meal,
        household_size=2,
        preferences={"diet": "veg"}
    )
    for item in result:
        print(f"  {item['name']}: {item['quantity']} {item['unit']}")
