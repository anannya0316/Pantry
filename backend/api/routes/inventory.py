from fastapi import (
    APIRouter,
    Header,
    BackgroundTasks
)

from models.inventory_models import (
    AddInventoryRequest,
    ClassifyRequest,
    UpdateInventoryItem,
    UseRecipeRequest
)

from services.inventory_service import (
    classify_inventory_item,
    reclassify_inventory,
    update_inventory_item,
    add_inventory_items,
    get_inventory
)

from services.low_stock_service import (
    get_low_stock_items
)

from services.inventory_recipe_service import (
    use_recipe
)

router = APIRouter()


@router.post("/classify")
def classify_endpoint(
    request: ClassifyRequest,
    user_id: str = Header(None)
):
    return classify_inventory_item(
        request,
        user_id
    )


@router.post("/reclassify")
def reclassify_endpoint(
    user_id: str = Header(None)
):
    return reclassify_inventory(user_id)


@router.put("/update")
def update_inventory_endpoint(
    request: UpdateInventoryItem,
    user_id: str = Header(None)
):
    return update_inventory_item(
        request,
        user_id
    )


@router.post("/add")
def add_inventory_endpoint(
    request: AddInventoryRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None)
):
    return add_inventory_items(
        request,
        background_tasks,
        user_id
    )


@router.get("/")
def get_inventory_endpoint(
    user_id: str = Header(None)
):
    return get_inventory(user_id)


@router.get("/low-stock")
def low_stock_endpoint(
    user_id: str = Header(None)
):
    return get_low_stock_items(user_id)


@router.post("/use-recipe")
def use_recipe_endpoint(
    request: UseRecipeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None)
):
    return use_recipe(
        request,
        background_tasks,
        user_id
    )