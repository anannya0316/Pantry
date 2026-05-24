import json
import logging

from utils.prompt_loader import load_prompt
from utils.web_search import tavily_search
from utils.llm_client import get_api_key, call_llm

logger = logging.getLogger(__name__)


def _call_llm(prompt: str) -> dict | None:
    try:
        content = call_llm(prompt, temperature=0, timeout=15)
    except Exception as e:
        logger.error(f"[classify] call_llm failed: {e}")
        return None

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    return json.loads(content)


def classify_item(
    item_name: str,
    household_size: int = 2,
):
    if not get_api_key():
        return {"display_name": item_name.lower(), "category": "Other", "quantity": 1, "unit": "unit"}

    prompt_template = load_prompt("classify.txt")

    def build_prompt(web_context: str = "") -> str:
        context_block = (
            f"\nWeb search context:\n{web_context}\n"
            if web_context else ""
        )
        return prompt_template.format(
            item_name=item_name,
            household_size=household_size,
            web_context=context_block,
        )

    try:
        logger.info(f"[classify] item='{item_name}' household_size={household_size}")

        parsed = _call_llm(build_prompt())
        logger.info(f"[classify] initial LLM response: {parsed}")

        if not parsed:
            logger.warning(f"[classify] LLM returned nothing for '{item_name}', falling back to Other")
            return {"display_name": item_name.lower(), "category": "Other", "quantity": 1, "unit": "unit"}

        recognized_name = parsed.get(
            "display_name",
            item_name.lower()
        )

        if parsed.get("category") == "Other":
            logger.info(f"[classify] category is Other for '{recognized_name}', triggering web search")
            web_context = tavily_search(
                f"{item_name} vegetable ingredient food Indian"
            )
            if web_context:
                parsed = _call_llm(
                    build_prompt(web_context)
                ) or parsed
                logger.info(f"[classify] post-web-search LLM response: {parsed}")

        result = {
            "display_name": parsed.get(
                "display_name",
                item_name.lower(),
            ),
            "category": parsed.get("category", "Other"),
            "quantity": parsed.get("quantity", 1),
            "unit": parsed.get("unit", "unit"),
        }
        logger.info(f"[classify] final result: {result}")
        return result

    except Exception as exc:
        logger.error(f"[classify] error for '{item_name}': {exc}")
        return {"display_name": item_name.lower(), "category": "Other", "quantity": 1, "unit": "unit"}
