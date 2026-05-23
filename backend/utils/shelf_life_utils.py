import re

from constants.shelf_life_constants import (
    DEFAULT_SHELF_LIFE_DAYS
)


def extract_shelf_life_days(
    response_text: str
) -> int:

    match = re.search(
        r"\d+",
        response_text
    )

    if not match:
        return DEFAULT_SHELF_LIFE_DAYS

    try:
        return int(match.group())

    except Exception:
        return DEFAULT_SHELF_LIFE_DAYS