import uuid
from contextlib import ExitStack
from unittest.mock import patch

from chatbot.agent import run_agent

TEST_USER_ID = "test_user"

_DEFAULT_MOCK_PROFILE = {
    "_id": TEST_USER_ID,
    "user_id": TEST_USER_ID,
    "name": "Test User",
    "household_size": 2,
    "diet": "non_veg",
}

def _mock_classify(display_name, **_):
    return {"display_name": display_name.title(), "category": "Other"}


def run_single_turn(user_input: str, mock_inventory=None, chat_id: str = None) -> dict:
    """Run one user turn with mocked DB. Returns the run_agent debug dict.

    called_tools entries: {"tool_name": str, "arguments": dict}
    """
    _chat_id = chat_id or f"test-{uuid.uuid4().hex[:8]}"

    with ExitStack() as stack:
        stack.enter_context(patch("chatbot.tools.inventory.get_profile", return_value=_DEFAULT_MOCK_PROFILE))
        stack.enter_context(patch("chatbot.tools.inventory.classify_item", side_effect=_mock_classify))
        stack.enter_context(patch("chatbot.tools.inventory.push_inventory_items", return_value=None))
        stack.enter_context(patch("chatbot.tools.inventory.update_inventory", return_value=None))

        if mock_inventory is not None:
            stack.enter_context(patch(
                "chatbot.tools.inventory.get_user_inventory",
                return_value={"items": mock_inventory},
            ))
        else:
            stack.enter_context(patch(
                "chatbot.tools.inventory.get_user_inventory",
                return_value={"items": []},
            ))

        return run_agent(
            user_message=user_input,
            user_id=TEST_USER_ID,
            debug=True,
            chat_id=_chat_id,
        )


def last_tool_calls(result: dict) -> list:
    """Return called_tools from a run_agent debug result.

    Each entry: {"tool_name": str, "arguments": dict}
    """
    return result.get("called_tools", [])


def last_text_reply(result: dict) -> str | None:
    """Return the final text response from a run_agent debug result."""
    return result.get("text")
