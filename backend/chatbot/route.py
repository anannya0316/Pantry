from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from chatbot.agent import run_agent
from utils.tracer import new_trace

router = APIRouter()


class SuggestRequest(BaseModel):
    query: str
    history: List[Dict[str, Any]] = []
    chat_id: Optional[str] = None


@router.get("/shopping-list/download")
def download_shopping_list(user_id: str = Header(None)):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id header is required")

    from chatbot.tools.shopping import get_shopping_list
    result = get_shopping_list(user_id=user_id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate shopping list"))

    shopping_list = result.get("shopping_list", [])
    if not shopping_list:
        content = "Your pantry is fully stocked! Nothing to buy right now."
    else:
        lines = ["Shopping List", "=" * 30, ""]
        sections = {
            "Out of stock":         [i for i in shopping_list if i["reason"] == "out of stock"],
            "Expired (replace)":    [i for i in shopping_list if i["reason"] == "expired"],
            "Running low":          [i for i in shopping_list if i["reason"] == "low stock"],
            "Needed for meal plan": [i for i in shopping_list if i["reason"] == "needed for meal plan"],
        }
        for heading, items in sections.items():
            if not items:
                continue
            lines.append(f"{heading}:")
            for item in items:
                detail = f" ({item['quantity']} {item['unit']} left)" if item.get("quantity") else ""
                lines.append(f"  - {item['name']}{detail}")
            lines.append("")
        content = "\n".join(lines)

    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": "attachment; filename=shopping_list.txt"},
    )


@router.post("/suggest")
def suggest(
    request: SuggestRequest,
    user_id: str = Header(None),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id header is required")

    trace = new_trace(user_id)
    trace.request_received(request.query)

    result = run_agent(
        user_message=request.query,
        user_id=user_id,
        debug=True,
        history=request.history or None,
        trace=trace,
        chat_id=request.chat_id,
    )

    tool_name = result.get("tool_name")
    text = result.get("text", "")
    success = result.get("success")
    recipes = result.get("recipes")
    shopping_list = result.get("shopping_list")

    INVENTORY_MUTATING_TOOLS = {"add_inventory_item", "update_inventory_item"}

    if tool_name in INVENTORY_MUTATING_TOOLS:
        response_type = "inventory_update"
    elif tool_name == "suggest_recipes" and recipes:
        response_type = "recipe"
    else:
        response_type = "chat"

    trace.response_sent(response_type=response_type, text_length=len(text))

    return {
        "type": response_type,
        "data": (
            recipes if response_type == "recipe"
            else shopping_list if response_type == "shopping_list"
            else None
        ),
        "text": text,
        "success": success,
        "chat_id": request.chat_id,
    }
