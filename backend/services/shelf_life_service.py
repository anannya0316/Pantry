from dao.shelf_life_dao import (
    get_shelf_life_doc,
    upsert_shelf_life
)

from services.llm_service import (
    generate_shelf_life
)

from utils.datetime_utils import now_ist


def fetch_shelf_life(
    item_name: str
):
    key = item_name.strip().lower()

    doc = get_shelf_life_doc(
        key
    )

    if not doc:
        return None

    return doc.get(
        "shelf_life_days"
    )


def store_shelf_life(
    item_name: str,
    shelf_life_days: int
):
    key = item_name.strip().lower()

    upsert_shelf_life(
        item_key=key,
        shelf_life_days=shelf_life_days,
        updated_at=now_ist().isoformat()
    )


def get_shelf_life(
    item_name: str
) -> int:

    existing = fetch_shelf_life(
        item_name
    )

    if existing is not None:
        return existing

    shelf_life_days = generate_shelf_life(
        item_name
    )

    store_shelf_life(
        item_name,
        shelf_life_days
    )

    return shelf_life_days