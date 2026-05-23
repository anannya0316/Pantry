from constants.shelf_life_constants import (
    DEFAULT_SHELF_LIFE_DAYS
)

from utils.shelf_life_utils import (
    extract_shelf_life_days
)

from utils.prompt_loader import load_prompt
from utils.llm_client import get_api_key, call_llm


def generate_shelf_life(
    item_name: str
) -> int:

    if not get_api_key():
        return DEFAULT_SHELF_LIFE_DAYS

    prompt_template = load_prompt(
    "shelf_life.txt"
    )

    prompt = prompt_template.format(
    item_name=item_name
    )

    try:
        content = call_llm(
            prompt,
            temperature=0.1,
            timeout=15,
        )

        return extract_shelf_life_days(
            content
        )

    except Exception as exc:

        print(
            f"generate_shelf_life error: "
            f"{exc}"
        )

        return DEFAULT_SHELF_LIFE_DAYS