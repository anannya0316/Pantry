import json
import os
from datetime import datetime
from typing import Literal, Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END, MessagesState

from utils.text_utils import clean_markdown
import chatbot.tools.inventory as _inv
import chatbot.tools.profile as _prof
import chatbot.tools.meal_plan as _mp
import chatbot.tools.nutrition as _nutr
import chatbot.tools.recipes as _rec
import chatbot.tools.shopping as _shop
from chatbot.tools.inventory import AddInventoryItemInput, UpdateInventoryItemInput
from chatbot.tools.meal_plan import AddMealPlanItemInput, UpdateMealPlanItemInput, GetMealPlanItemInput
from chatbot.tools.profile import UpdateProfileInput
from chatbot.tools.nutrition import LogRecipeInput, GetNutritionLogByMealInput
from chatbot.tools.shopping import GetShoppingListInput
_today = datetime.now().strftime("%A, %Y-%m-%d")


def _make_model() -> ChatOpenAI:
    return ChatOpenAI(
        model="deepseek/deepseek-v4-flash",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPEN_ROUTER_KEY"),
        temperature=0,
        max_tokens=1024,
    )


# ── Tool factories (bind user_id via closure) ────────────────────────────────

def _make_inventory_tools(user_id: str):
    @tool(args_schema=AddInventoryItemInput)
    def add_inventory_item(
        display_name: str,
        quantity: Optional[int] = None,
        unit: Optional[str] = None,
        category: Optional[str] = None,
        purchase_date: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Add a new item to inventory. If quantity or unit are not given, ask the user before calling this tool."""
        return _inv.add_inventory_item(
            user_id=user_id,
            display_name=display_name,
            quantity=quantity,
            unit=unit,
            category=category,
            purchase_date=purchase_date,
            status=status,
        )

    @tool(args_schema=UpdateInventoryItemInput)
    def update_inventory_item(
        display_name: str,
        quantity: Optional[int] = None,
        unit: Optional[str] = None,
        category: Optional[str] = None,
        purchase_date: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Update an existing inventory item. Only the fields provided will be changed."""
        return _inv.update_inventory_item(
            user_id=user_id,
            display_name=display_name,
            quantity=quantity,
            unit=unit,
            category=category,
            purchase_date=purchase_date,
            status=status,
        )

    @tool
    def get_all_inventory_items() -> dict:
        """Fetch all items currently in the user's inventory."""
        return _inv.get_all_inventory_items(user_id=user_id)

    return [add_inventory_item, update_inventory_item, get_all_inventory_items]


def _make_meal_plan_tools(user_id: str):
    @tool(args_schema=GetMealPlanItemInput)
    def get_meal_plan_item(
        meal_name: Optional[str] = None,
        meal_day: Optional[str] = None,
        meal_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Fetch meals from the meal plan. Pass meal_day or meal_type to filter; omit all to get the full plan."""
        return _mp.get_meal_plan_item(user_id=user_id, meal_name=meal_name, meal_day=meal_day, meal_type=meal_type, status=status)

    @tool(args_schema=UpdateMealPlanItemInput)
    def update_meal_plan_item(
        meal_name: str,
        meal_day: Optional[str] = None,
        meal_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Update an existing meal plan entry. Pass the new day or meal_type to reschedule."""
        return _mp.update_meal_plan_item(
            user_id=user_id,
            meal_name=meal_name,
            meal_day=meal_day,
            meal_type=meal_type,
            status=status,
        )

    @tool(args_schema=AddMealPlanItemInput)
    def add_meal(
        meal_name: str,
        meal_day: str,
        meal_type: str,
        created_at: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """Add a new meal to the weekly plan. meal_day must be a full weekday name (Monday–Sunday). meal_type must be 'breakfast', 'lunch', 'dinner', or 'snack'."""
        return _mp.add_meal(user_id=user_id, meal_name=meal_name, meal_day=meal_day, meal_type=meal_type, created_at=created_at, status=status)

    return [get_meal_plan_item, update_meal_plan_item, add_meal]


def _make_profile_tools(user_id: str):
    @tool
    def get_profile() -> dict:
        """Fetch the user's full profile."""
        return _prof.get_profile(user_id=user_id)

    @tool(args_schema=UpdateProfileInput)
    def update_profile(
        household_size: Optional[int] = None,
        cooking_frequency: Optional[str] = None,
        grocery_shopping_day: Optional[str] = None,
        diet: Optional[str] = None,
        goals: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        spice_preference: Optional[str] = None,
        liked_ingredients: Optional[List[str]] = None,
        disliked_ingredients: Optional[List[str]] = None,
        favorite_cuisines: Optional[List[str]] = None,
        special_preferences: Optional[List[str]] = None,
    ) -> dict:
        """Update one or more fields of the user's profile. Name and phone cannot be changed — do not attempt to update them."""
        return _prof.update_profile(
            user_id=user_id,
            household_size=household_size,
            cooking_frequency=cooking_frequency,
            grocery_shopping_day=grocery_shopping_day,
            diet=diet,
            goals=goals,
            allergies=allergies,
            spice_preference=spice_preference,
            liked_ingredients=liked_ingredients,
            disliked_ingredients=disliked_ingredients,
            favorite_cuisines=favorite_cuisines,
            special_preferences=special_preferences,
        )

    return [get_profile, update_profile]


def _make_nutrition_tools(user_id: str):
    @tool(args_schema=LogRecipeInput)
    def log_recipe(meal_name: str, meal_type: str) -> dict:
        """Log nutrition and health score for a meal the user explicitly says they just ate. meal_name MUST come from what the user said — never infer from memory or meal plan. meal_type must be 'breakfast', 'lunch', 'dinner', or 'snack'."""
        return _nutr.log_recipe(user_id=user_id, meal_name=meal_name, meal_type=meal_type)

    @tool
    def get_all_nutrition_logs() -> dict:
        """Fetch all nutrition log entries for the user."""
        return _nutr.get_all_nutrition_logs(user_id=user_id)

    @tool(args_schema=GetNutritionLogByMealInput)
    def get_nutrition_log_by_meal(meal_name: str) -> dict:
        """Fetch nutrition log entries for a specific meal by name. Case-insensitive partial match."""
        return _nutr.get_nutrition_log_by_meal_name(user_id=user_id, meal_name=meal_name)

    return [log_recipe, get_all_nutrition_logs, get_nutrition_log_by_meal]


def _make_recipe_tools(user_id: str):
    @tool
    def suggest_recipes(preferences: Optional[str] = None) -> dict:
        """Generate recipe suggestions using the user's inventory and full profile (diet, allergies, spice preference, etc.).
        Pass any extra context as `preferences` — e.g. a specific dish name, guest count ("for 8 guests"), or occasion.
        Do NOT call get_all_inventory_items or get_profile first; this tool fetches them internally."""
        return _rec.suggest_recipes(user_id=user_id, preferences=preferences)

    return [suggest_recipes]


def _make_shopping_tools(user_id: str):
    @tool(args_schema=GetShoppingListInput)
    def get_shopping_list() -> dict:
        """Generate a shopping list from the user's meal plan and current inventory.
        Returns out-of-stock, expired, low-stock items, and ingredients needed for planned meals."""
        return _shop.get_shopping_list(user_id=user_id)

    return [get_shopping_list]


# ── Supervisor ───────────────────────────────────────────────────────────────

class _Route(BaseModel):
    next: Literal["inventory", "meal_plan", "profile", "nutrition_log", "recipe", "shopping_list"]


_SUPERVISOR_SYSTEM = f"""You are a routing assistant. Given the conversation, decide which specialist agent should handle the user's latest message.

Today is {_today}.

Agents:
- inventory: raw ingredient stock — quantities, units, restocking, checking what's in store.
  Use this when the user mentions having, buying, or updating a quantity of an ingredient.
- meal_plan: weekly meal schedule — viewing, adding, or updating planned meals.
- profile: user profile — name, diet, allergies, goals, shopping day, household size, cooking frequency.
- nutrition_log: logging a meal the user already ate, OR clarifying an ambiguous food mention with no quantity context.
  Do NOT use this for messages that mention a quantity of a raw ingredient — those are inventory.
- recipe: generating a recipe for a specific meal, including what ingredients the user has and what they need to buy.
- shopping_list: generating a shopping list from the weekly meal plan vs. current inventory — no specific meal mentioned.

When in doubt between meal_plan and nutrition_log, choose nutrition_log — it will ask the user to clarify.
Reply with only the agent name."""


# ── Graph builder ─────────────────────────────────────────────────────────────

def _build_app(user_id: str):
    """Build and compile a LangGraph supervisor app with user-specific tools."""
    inventory_agent = create_react_agent(
        _make_model(),
        tools=_make_inventory_tools(user_id),
        prompt=f"""You are an inventory assistant for a small store.
Only answer questions related to inventory management. Today is {_today}.
- NEVER fake actions. Only report success after calling a tool.
- NEVER invent quantity or unit values — ask if missing.
- Parse combined quantity+unit (e.g. "500 g") directly and call the tool immediately.
- Only call inventory for raw ingredients not meals. If the user is asking about meals, direct them to the meal planning agent or nutrition log agent.
""",
    )

    meal_plan_agent = create_react_agent(
        _make_model(),
        tools=_make_meal_plan_tools(user_id),
        prompt=f"""You are a meal planning assistant.
Only answer questions related to meal planning.
Today is {_today}.
- NEVER fake actions. Only report success after calling a tool.
- The meal plan only supports breakfast, lunch, and dinner. If the user asks to add a snack or any other meal type, tell them it cannot be added to the meal plan and suggest they log it via the nutrition log instead.
""",
    )

    profile_agent = create_react_agent(
        _make_model(),
        tools=_make_profile_tools(user_id),
        prompt="""You are a profile assistant.
Only answer questions related to the user's profile like name, phone, household size, cooking frequency, shopping day, allergies, diet, and goals.
- NEVER fake actions. Only report success after calling a tool.
- Name and phone cannot be changed — tell the user if they ask.
""",
    )

    nutrition_log_agent = create_react_agent(
        _make_model(),
        tools=_make_nutrition_tools(user_id),
        prompt=f"""You are a nutrition assistant. You log meals that are NOT part of the user's meal plan — unplanned or substitute meals.
Today is {_today}.
- NEVER say you have logged a meal unless you actually called log_recipe.
- NEVER invent or assume meal_name or meal_type — ask if missing.
- If the user just mentions a food or meal name without context (e.g. "dal rice", "pasta"), ask:
  "Would you like to log [food] as a meal you had, or add it to your meal plan?"
  Wait for their answer before taking any action.
- ONLY call log_recipe when the user clearly mentions eating a meal that is not planned:
  - Examples: "I had grilled chicken salad for dinner", "I skipped my lunch and ate pizza instead".
- If it is unclear whether the meal is planned or unplanned, ask the user before calling log_recipe.
""",
    )

    recipe_agent = create_react_agent(
        _make_model(),
        tools=_make_recipe_tools(user_id),
        prompt=f"""You are a recipe assistant. Generate recipes and show the user what ingredients they have and what they still need.
Today is {_today}.
- Always call suggest_recipes when the user asks for a recipe or cooking ideas.
- Present the result clearly: ingredients list, steps, then what they have vs. what they need to buy.
- NEVER fabricate a recipe without calling the tool.
""",
    )

    shopping_list_agent = create_react_agent(
        _make_model(),
        tools=_make_shopping_tools(user_id),
        prompt=f"""You are a shopping assistant. Generate a shopping list for the user.
Today is {_today}.
- Call get_shopping_list to retrieve the full shopping list.
- Present the result clearly: out-of-stock items, low-stock items, and ingredients needed for the meal plan.
- NEVER guess what's needed without calling the tool first.
""",
    )

    supervisor_model = _make_model().with_structured_output(_Route)

    def supervisor(state):
        result = supervisor_model.invoke([
            SystemMessage(content=_SUPERVISOR_SYSTEM),
            *state["messages"],
        ])
        return {"next": result.next}

    class State(MessagesState):
        next: str = ""

    def _call_agent(agent, state):
        response = agent.invoke({"messages": state["messages"]})
        return {"messages": response["messages"][len(state["messages"]):]}

    graph = StateGraph(State)
    graph.add_node("supervisor", supervisor)
    graph.add_node("inventory",     lambda s: _call_agent(inventory_agent, s))
    graph.add_node("meal_plan",     lambda s: _call_agent(meal_plan_agent, s))
    graph.add_node("profile",       lambda s: _call_agent(profile_agent, s))
    graph.add_node("nutrition_log", lambda s: _call_agent(nutrition_log_agent, s))
    graph.add_node("recipe",        lambda s: _call_agent(recipe_agent, s))
    graph.add_node("shopping_list", lambda s: _call_agent(shopping_list_agent, s))

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", lambda s: s["next"], {
        "inventory":     "inventory",
        "meal_plan":     "meal_plan",
        "profile":       "profile",
        "nutrition_log": "nutrition_log",
        "recipe":        "recipe",
        "shopping_list": "shopping_list",
    })
    for node in ("inventory", "meal_plan", "profile", "nutrition_log", "recipe", "shopping_list"):
        graph.add_edge(node, END)

    return graph.compile()


# ── Debug data extraction ─────────────────────────────────────────────────────

def _extract_debug_data(messages, prev_count: int):
    called_tools = []
    recipes = None
    last_success = None

    for msg in messages[prev_count:]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                called_tools.append({"tool_name": tc["name"], "arguments": tc["args"]})
        elif isinstance(msg, ToolMessage):
            try:
                result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                last_success = result.get("success")
                if msg.name == "suggest_recipes" and result.get("success"):
                    recipes = result.get("recipes")
            except (json.JSONDecodeError, AttributeError):
                pass

    return called_tools, recipes, last_success


# ── Public API ────────────────────────────────────────────────────────────────

def run_agent(
    user_message: str,
    user_id: str,
    debug: bool = False,
    history: list = None,
    trace=None,
    tools: list | None = None,
    tool_choice: str = "auto",
    chat_id: str | None = None,
):
    """Invoke the LangGraph supervisor agent and return a response."""
    app = _build_app(user_id)

    messages = []
    for msg in (history or []):
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            messages.append(("user", content))
        elif role == "assistant":
            messages.append(("assistant", content))

    prev_count = len(messages)
    messages.append(("user", user_message))

    result = app.invoke({"messages": messages})

    all_messages = result.get("messages", [])
    called_tools, recipes, last_success = _extract_debug_data(all_messages, prev_count)

    last_tool_name = called_tools[-1]["tool_name"] if called_tools else None
    final_text = clean_markdown(all_messages[-1].content if all_messages else "")

    if trace:
        for ct in called_tools:
            trace.tool_called(ct["tool_name"], ct["arguments"])

    if debug:
        msg_list = []
        for m in all_messages:
            if hasattr(m, "type"):
                if m.type == "human":
                    msg_list.append({"role": "user", "content": m.content})
                elif m.type == "ai" and not getattr(m, "tool_calls", None):
                    msg_list.append({"role": "assistant", "content": m.content})

        return {
            "text": final_text,
            "tool_name": last_tool_name,
            "success": last_success if last_success is not None else (True if called_tools else None),
            "called_tools": called_tools,
            "messages": msg_list,
            "recipes": recipes,
            "shopping_list": None,
        }

    return final_text
