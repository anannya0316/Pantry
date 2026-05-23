from fastapi import (
    APIRouter,
    HTTPException
)

from services.shelf_life_service import (
    get_shelf_life
)

router = APIRouter()


@router.get("/")
def get_shelf_life_route(
    item_name: str
):
    if not item_name:
        raise HTTPException(
            status_code=400,
            detail="item_name required"
        )

    return {
        "item_name": item_name,
        "shelf_life_days": get_shelf_life(
            item_name
        )
    }