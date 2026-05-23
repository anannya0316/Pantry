from fastapi import (
    APIRouter,
    BackgroundTasks,
    Header,
)

from models.meal_models import (
    AddMealRequest,
    DeleteMealRequest,
)

from services.meal_service import (
    get_meal_plan_service,
    add_meal,
    delete_meal,
)

router = APIRouter()


@router.get("/")
def get_meal_plan_route(
    background_tasks: BackgroundTasks,
    user_id: str = Header(None),
):
    return get_meal_plan_service(
        background_tasks,
        user_id,
    )


@router.post("/add")
def add_meal_route(
    request: AddMealRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Header(None),
):
    return add_meal(
        request,
        background_tasks,
        user_id,
    )


@router.post("/delete")
def delete_meal_route(
    request: DeleteMealRequest,
    user_id: str = Header(None),
):
    return delete_meal(
        request,
        user_id,
    )