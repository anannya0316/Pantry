import json

from utils.prompt_loader import load_prompt
from utils.web_search import tavily_search
from utils.llm_client import get_api_key, call_llm


def _call_llm(prompt: str) -> dict | None:
    try:
        content = call_llm(prompt, temperature=0, timeout=15)
    except Exception:
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
        return {"category": "Other"}

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
        parsed = _call_llm(build_prompt())
        if not parsed:
            return {"category": "Other"}

        recognized_name = parsed.get(
            "display_name",
            item_name.lower()
        )

        if recognized_name == item_name.strip().lower():
            web_context = tavily_search(
                f"{item_name} vegetable ingredient food Indian"
            )
            if web_context:
                parsed = _call_llm(
                    build_prompt(web_context)
                ) or parsed

        return {
            "display_name": parsed.get(
                "display_name",
                item_name.lower(),
            ),
            "category": parsed.get("category", "Other"),
            "quantity": parsed.get("quantity", 1),
            "unit": parsed.get("unit", "unit"),
        }

    except Exception as exc:
        print(f"classify_item error: {exc}")
        return {"category": "Other"}
