VALID_UNITS = {
    "unit",
    "kg",
    "g",
    "liter",
    "ml",
    "pieces",
    "lbs",
    "loaf"
}


UNIT_MAP = {
    "cup": "ml",
    "cups": "ml",
    "tbsp": "ml",
    "tablespoon": "ml",
    "tablespoons": "ml",
    "tsp": "ml",
    "teaspoon": "ml",
    "teaspoons": "ml",
    "l": "liter",
    "litre": "liter",
    "litres": "liter",
    "liters": "liter",
    "gram": "g",
    "grams": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "lb": "lbs",
    "pound": "lbs",
    "pounds": "lbs",
    "oz": "g",
    "ounce": "g",
    "ounces": "g",
    "piece": "pieces",
    "pcs": "pieces",
    "slice": "pieces",
    "slices": "pieces",
    "bunch": "unit",
    "handful": "unit",
    "clove": "pieces",
    "cloves": "pieces",
    "loaves": "loaf",
}


def normalize_unit(unit: str) -> str:
    u = unit.strip().lower()

    if u in VALID_UNITS:
        return u

    return UNIT_MAP.get(u, "unit")