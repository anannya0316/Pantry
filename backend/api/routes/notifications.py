from fastapi import APIRouter, Header

from services.notifications_service import get_notifications

router = APIRouter()


@router.get("/")
def get_notifications_route(user_id: str = Header(None)):
    if not user_id:
        return []
    return get_notifications(user_id)
