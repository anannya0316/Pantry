# PANTRY — CURRENT SYSTEM MAP

## Stack
- **Backend:** Python / FastAPI / MongoDB
- **Frontend:** React 19 / Vite / TailwindCSS
- **LLM (chatbot agent):** OpenRouter `deepseek/deepseek-v4-flash` via `langchain_openai.ChatOpenAI`
- **LLM (utility calls):** OpenRouter `openai/gpt-4o-mini` via `utils/llm_client.py` (classification, shelf life, nutrition, ingredients, low stock, recipes)
- **Auth:** `user_id` header (UUID), Google OAuth, email verification
- **Search:** Tavily (fallback in classification & ingredient extraction services only)
- **Agent memory:** LangGraph `MemorySaver` (in-process, keyed by `chat_id` or `user-{user_id}`)

---

## API Routes

| Method | Path | Handler |
|--------|------|---------|
| POST | `/auth/create-account` | `create_account()` |
| POST | `/auth/login` | `login_user()` |
| POST | `/auth/verify-email` | `verify_email()` |
| POST | `/auth/google` | `google_auth()` |
| GET | `/auth/check-verification` | `check_verification()` |
| POST | `/auth/complete-onboarding` | `complete_onboarding()` |
| GET | `/profile/` | `get_user_profile()` |
| PUT | `/profile/update-goals` | `update_user_goals()` |
| PUT | `/profile/update` | `update_user_profile()` |
| GET | `/profile/insights` | `get_profile_insights()` |
| POST | `/inventory/classify` | `classify_inventory_item()` |
| POST | `/inventory/reclassify` | `reclassify_inventory()` |
| PUT | `/inventory/update` | `update_inventory_item()` |
| POST | `/inventory/add` | `add_inventory_items()` |
| GET | `/inventory/` | `get_inventory()` |
| GET | `/inventory/low-stock` | `get_low_stock_items()` |
| POST | `/inventory/use-recipe` | `use_recipe()` |
| GET | `/meal-plan/` | `get_meal_plan_service()` |
| POST | `/meal-plan/add` | `add_meal()` |
| POST | `/meal-plan/delete` | `delete_meal()` |
| POST | `/nutrition/log-recipe` | `log_recipe_background()` |
| GET | `/nutrition/insights` | `get_nutrition_insights()` |
| POST | `/recipes/suggest` | `suggest()` (chatbot entry point) |
| GET | `/recipes/shopping-list/download` | `download_shopping_list()` (plain text file) |
| GET | `/shelf-life/` | `get_shelf_life()` |
| POST | `/onboarding/complete-onboarding` | `complete_onboarding()` |
| GET | `/notifications/` | `get_notifications()` |

---

## DB Collections & Key Fields

| Collection | Key Fields |
|------------|-----------|
| `users` | `_id`, `email`, `password`, `google_id`, `verified` |
| `profiles` | `user_id`, `name`, `phone`, `household_size`, `cooking_frequency`, `diet`, `spice_preference`, `goals`, `allergies`, `grocery_shopping_day`, liked/disliked ingredients, cuisines, special_preferences |
| `inventory` | `user_id`, `items[]` → `display_name`, `quantity`, `unit`, `category`, `aliases`, `status`, `purchase_date` |
| `meal_plans` | `user_id`, `meals{Day}{breakfast\|lunch\|dinner}[]` → `meal_name`, `ingredients[]`, `nutrition{}`, `consumed`, `skipped`, `valid` |
| `nutrition_logs` | `user_id`, `meal`, `meal_type`, `nutrition{}`, `health_score`, `created_at` |
| `pending_registrations` | `email`, `verification_token`, `verification_token_expires` |
| `shelf_life` | `item_key`, `shelf_life_days` |
| `agent_events` | `user_id`, `timestamp`, `event_type`, `payload` (used by memory_service for recent context) |
| `chats` | (reserved) |
| `chat_messages` | (reserved) |
| `recipe_memory` | (reserved) |

---

## Where AI Is Called

| File | Function | Prompt | Purpose |
|------|----------|--------|---------|
| `services/classification_service.py` | `classify_item()` | `prompts/classify.txt` | Normalize name, assign category, estimate quantity |
| `services/llm_service.py` | `generate_shelf_life()` | `prompts/shelf_life.txt` | Days until item goes stale |
| `services/nutrition_service.py` | `fetch_nutrition()` | `prompts/nutrition.txt` | Per-serving macro/micro nutrition |
| `services/ingredient_service.py` | `fetch_ingredients()` | `prompts/ingredient_extraction.txt` | Ingredients for a meal given household prefs |
| `services/low_stock_service.py` | `get_low_stock_items()` | `prompts/low_stock.txt` | Which items will run out before next shop |
| `chatbot/tools/recipes.py` | `suggest_recipes()` | `prompts/recipe_suggestion.txt` | Suggest recipes from current inventory |
| `chatbot/agent.py` | `_make_model()` / supervisor | inline system prompts | LangGraph supervisor routes to specialist subagents; each subagent runs its own ReAct loop |

---

## Chatbot Architecture

Entry point: `POST /recipes/suggest → chatbot/route.py → suggest()`

### Overview

The chatbot uses a **LangGraph supervisor multi-agent** architecture. A supervisor LLM classifies each message into one of six specialist agents; the selected agent then runs a ReAct loop with its own tools and system prompt. Conversation history is persisted in-process via `MemorySaver`, keyed by `chat_id`.

### Request Flow

```
POST /recipes/suggest (query, history?, chat_id?)
  → run_agent(user_message, user_id, debug=True, chat_id)

  LangGraph graph (compiled with MemorySaver):
    supervisor node
      → structured-output LLM classifies message → one of:
          "inventory" | "meal_plan" | "profile" | "nutrition_log" | "recipe" | "shopping_list"
      → route to specialist node

    specialist node (create_react_agent)
      → ReAct loop with specialist tools + system prompt
      → returns new messages

  → extract last AI text + called tools from message list
  → classify response_type: "inventory_update" | "recipe" | "chat"
  → return {type, data, text, success, chat_id}
```

### Supervisor (`chatbot/agent.py` — `_SUPERVISOR_SYSTEM`)

Structured-output LLM call using `_Route` Pydantic model with field `next`. Routes to:

| Agent | Trigger |
|-------|---------|
| `inventory` | Raw ingredient stock — quantities, buying, restocking |
| `meal_plan` | Weekly meal schedule — viewing, adding, updating |
| `profile` | Name, diet, allergies, goals, shopping day, household size, cooking frequency |
| `nutrition_log` | Logging a meal already eaten, or ambiguous food mention without quantity context |
| `recipe` | Generating a recipe for a specific meal |
| `shopping_list` | Generating a shopping list from meal plan vs. inventory |

### Specialist Agents (each via `create_react_agent`)

Each agent gets a dedicted system prompt injected with today's date. All agents share the same model (`deepseek/deepseek-v4-flash`). Tools are created per-request via closure factories (`_make_*_tools(user_id)`).

Key agent rules:
- **inventory** — never invent quantity/unit; ask if missing; raw ingredients only, not meals
- **meal_plan** — supports only breakfast, lunch, dinner; no snacks; suggest nutrition log instead
- **profile** — name and phone cannot be changed
- **nutrition_log** — only calls `log_recipe` when user clearly states they just ate an unplanned meal; asks to clarify if ambiguous
- **recipe** — always calls `suggest_recipes`; never fabricates a recipe without calling the tool
- **shopping_list** — always calls `get_shopping_list` first; never guesses

### Chatbot Tools

Tools are bound per-request via factory functions. Each factory closes over `user_id`.

| Tool | Agent | Parameters | File | Effect |
|------|-------|-----------|------|--------|
| `add_inventory_item` | inventory | `display_name`, `quantity?`, `unit?`, `category?`, `purchase_date?`, `status?` | `tools/inventory.py` | Upserts item (fuzzy match → update existing, else classify via LLM + insert) |
| `update_inventory_item` | inventory | `display_name`, `quantity?`, `unit?`, `category?`, `purchase_date?`, `status?` | `tools/inventory.py` | Patches only provided fields; must exist |
| `get_all_inventory_items` | inventory | — | `tools/inventory.py` | Returns all inventory items |
| `get_meal_plan_item` | meal_plan | `meal_name?`, `meal_day?`, `meal_type?`, `status?` | `tools/meal_plan.py` | Returns full plan (filtering by params not implemented server-side) |
| `update_meal_plan_item` | meal_plan | `meal_name`, `meal_day?`, `meal_type?`, `status?` | `tools/meal_plan.py` | Reschedules meal (calls `add_meal_service` for new slot) |
| `add_meal` | meal_plan | `meal_name`, `meal_day`, `meal_type`, `created_at?`, `status?` | `tools/meal_plan.py` | Adds meal; spawns nutrition fetch in background thread |
| `get_profile` | profile | — | `tools/profile.py` | Returns profile + email |
| `update_profile` | profile | `household_size?`, `cooking_frequency?`, `grocery_shopping_day?`, `diet?`, `goals?[]`, `allergies?[]`, `spice_preference?`, `liked_ingredients?[]`, `disliked_ingredients?[]`, `favorite_cuisines?[]`, `special_preferences?[]` | `tools/profile.py` | Validates and patches profile; name/phone immutable |
| `log_recipe` | nutrition_log | `meal_name`, `meal_type` | `tools/nutrition.py` | Fetches nutrition, calculates health score, inserts nutrition log |
| `get_all_nutrition_logs` | nutrition_log | — | `tools/nutrition.py` | Returns all nutrition log entries |
| `get_nutrition_log_by_meal` | nutrition_log | `meal_name` | `tools/nutrition.py` | Case-insensitive partial match on meal name |
| `suggest_recipes` | recipe | `preferences?` | `tools/recipes.py` | Calls LLM with inventory + `recipe_suggestion.txt`; returns structured recipe array |
| `get_shopping_list` | shopping_list | — | `tools/shopping.py` | Deterministic (no LLM): out-of-stock + expired + low-stock + missing meal plan ingredients |

### Response Classification (`chatbot/route.py`)

After `run_agent` returns, `suggest()` classifies the response:

| Condition | `type` |
|-----------|--------|
| Last tool in `{add_inventory_item, update_inventory_item}` | `inventory_update` |
| Last tool = `suggest_recipes` AND recipes present | `recipe` |
| Otherwise | `chat` |

### Memory

LangGraph `MemorySaver` persists the full message history per thread in-process. Thread ID = `chat_id` (from request) or `user-{user_id}`. No DB persistence between server restarts.

### Tracer (`utils/tracer.py`)

`AgentTrace` — records LLM calls, tool calls, intent classification, and response dispatch. Created per request via `new_trace(user_id)`. Passed through the call chain.

---

## Key Flows

### Registration
```
POST /auth/create-account
  → insert pending_registrations
  → send verification email

User clicks link

POST /auth/verify-email (token)
  → create users doc
  → create profiles doc
  → create empty inventory doc
```

### Onboarding
```
POST /auth/complete-onboarding (household_items, goals)
  → for each item: classify_item() [LLM]
  → update profiles.goals
  → update inventory.items
  → background: get_shelf_life() for each item
```

### Add Inventory Item
```
POST /inventory/add (items[])
  → for each item:
      classify_item() [LLM] → normalize name, category, quantity
      deduplicate against existing inventory (exact + alias match)
      push to inventory.items
      background: get_shelf_life()
```

### Add Meal to Plan
```
POST /meal-plan/add (day, meal_type, meal_name)
  → get user profile (preferences)
  → fetch_ingredients() [LLM, Tavily fallback if empty]
  → match ingredients against current inventory (fuzzy)
  → add to meal_plans[day][meal_type][]
  → mark previous valid meal in slot as invalid
  → background: fetch_nutrition() [LLM]
```

### Get Meal Plan
```
GET /meal-plan
  → auto_consume_past_meals()
      past meals (since last grocery_shopping_day cycle) → mark consumed → deduct_ingredients() from inventory
      today's meals past cutoff (breakfast ≥ 8am, lunch ≥ 1pm, dinner ≥ 8pm IST) → mark consumed
  → run_weekly_restock()
      if new week since last_restock_week → restore inventory quantities from current plan's ingredients
  → return {meals, restocked}
```

### Chatbot — Single Turn
```
POST /recipes/suggest (query, chat_id?)
  → run_agent() → LangGraph graph
      supervisor classifies → specialist agent
      specialist ReAct loop → tool calls → final AI text
  → classify response_type
  → return {type, data, text, success, chat_id}
```

### Low Stock Detection
```
GET /inventory/low-stock
  → get all inventory items + household size + days until next shopping day
  → call LLM with low_stock.txt prompt
  → return list of low item names
```

### Log Meal (REST)
```
POST /nutrition/log-recipe (meal_name, meal_type?)
  → infer meal_type from IST hour if not provided (< 10 → breakfast, < 15 → lunch, else dinner)
  → background:
      fetch_nutrition() [LLM]
      get_daily_targets() from user goals
      calculate_meal_health_score()
      insert_nutrition_log()
```

### Use Recipe (deduct inventory)
```
POST /inventory/use-recipe (ingredients[], have[], need_to_buy[])
  → for each item in have[]: fuzzy match → deduct quantity from inventory
  → for each item in need_to_buy[]: add to inventory with qty=0
  → background: get_shelf_life() for new items
```

---

## Prompts

### `prompts/classify.txt`
- **Input:** item name + optional Tavily web context + household_size
- **Output:** `{"display_name": str, "category": str, "quantity": float, "unit": str}`
- **Categories:** Dairy, Protein, Produce, Grains, Nuts, Other

### `prompts/shelf_life.txt`
- **Input:** item name
- **Output:** single integer (days)

### `prompts/nutrition.txt`
- **Input:** meal name
- **Output:** `{"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0, "vitamin_c_mg": 0, "iron_mg": 0, "calcium_mg": 0}`
- Per serving / per person

### `prompts/ingredient_extraction.txt`
- **Input:** meal name + household size + user preferences + optional Tavily web context
- **Output:** `[{"name": str, "quantity": float, "unit": str}]`

### `prompts/low_stock.txt`
- **Input:** today's date + household size + grocery_shopping_day + days_until_shopping + full inventory JSON
- **Output:** `["item1", "item2", ...]`

### `prompts/recipe_suggestion.txt`
- **Input:** `{inventory}`, `{household_size}`, `{preferences_line}`
- **Output:** JSON array, exactly 1 recipe: `title`, `description`, `prep_time`, `cook_time`, `servings`, `ingredients[]`, `steps[]`, `have[]`, `need_to_buy[]`

---

## State Storage Summary

| State | Where Stored |
|-------|-------------|
| User auth | `users` collection |
| Preferences / goals | `profiles` collection |
| Current pantry | `inventory.items[]` |
| Weekly meal schedule | `meal_plans.meals` |
| Nutrition history | `nutrition_logs` |
| Shelf life cache | `shelf_life` collection |
| In-flight registration | `pending_registrations` |
| Recent meal events (memory) | `agent_events` collection |
| Agent conversation history | `MemorySaver` (in-process) — lost on server restart |
| Auth token | `user_id` request header (no JWT) |

---

## Key Implementation Notes

- **No JWT** — `user_id` UUID is passed directly as a request header
- **Inventory items are never deleted**, only quantity-deducted or marked consumed
- **Only one valid meal per slot** — adding a new meal marks the previous one invalid
- **Meal ingredients deducted only on consumption** (auto-consume on GET /meal-plan)
- **Weekly restock** restores inventory quantities based on current plan ingredients each new week
- **Auto-consume window** is anchored to the user's `grocery_shopping_day`, not just Monday
- **Fuzzy matching** (`rapidfuzz`) used throughout for ingredient ↔ inventory name resolution
- **Tavily web search** is a fallback for `classify_item` and `fetch_ingredients` only
- **LangGraph supervisor** routes each message to exactly one specialist agent; no fallback to general chat
- **`get_shopping_list` has no LLM call** — fully rule-based (thresholds per unit, inventory + meal plan cross-check)
- **Nutrition logging in chatbot** is synchronous (`log_recipe` calls `fetch_nutrition` inline)
- **Background tasks** used for shelf life fetch, nutrition logging from REST endpoints
- **`add_inventory_item` upserts** — fuzzy-matches existing item first; only inserts if not found
- **`clean_markdown()`** strips all markdown formatting from LLM output before sending to frontend (`utils/text_utils.py`)
- **Profile new fields** vs. original: `phone`, `cooking_frequency`, `spice_preference` added

---

## Directory Structure

```
backend/
  api/
    app.py               FastAPI app init
    router.py            Route registration
    middleware.py
    routes/
      auth.py
      profile.py
      inventory.py
      meal_plan.py
      nutrition.py
      shelf_life.py
      onboarding.py
      notifications.py
  chatbot/
    agent.py             LangGraph supervisor + 6 specialist subagents (ReAct), run_agent()
    route.py             POST /recipes/suggest + GET /recipes/shopping-list/download
    tools/
      inventory.py       add/update/get_all inventory item + Pydantic schemas
      meal_plan.py       get/add/update meal plan item + Pydantic schemas
      nutrition.py       log_recipe, get_all_nutrition_logs, get_nutrition_log_by_meal + schemas
      profile.py         get/update user profile + Pydantic schemas
      recipes.py         suggest_recipes
      shopping.py        get_shopping_list (deterministic, no LLM)
    evals/               Eval suite: inventory, meal_plan, meal_logging, profile evals + runner
    tests/               Unit tests for tools
  db/
    mongo.py
    collections.py
    indexes.py
  dao/
    inventory_dao.py
    profile_dao.py
    meal_dao.py
    nutrition_dao.py
    shelf_life_dao.py
  services/
    auth_service.py
    classification_service.py
    email_service.py
    health_score_service.py
    ingredient_service.py
    inventory_maintainance_service.py
    inventory_recipe_service.py
    inventory_service.py
    llm_service.py            (shelf life LLM wrapper)
    low_stock_service.py
    meal_inventory_service.py
    meal_service.py
    memory_service.py         record_meal_event, get_recent_context, get_top_meals
    notifications_service.py
    nutrition_insights_service.py
    nutrition_logging_service.py
    nutrition_service.py
    nutrition_target_service.py
    onboarding_service.py
    profile_insights_service.py
    profile_service.py
    shelf_life_service.py
  models/
    auth_models.py
    enums.py
    inventory_models.py
    meal_models.py
    nutrition_models.py
    onboarding_models.py
    profile_models.py
  constants/
    meal_constants.py
    nutrition_constants.py
    profile_constants.py
    shelf_life_constants.py
  jobs/
    auto_consume.py
    weekly_restock.py
  utils/
    llm_client.py        LLM provider config (OpenRouter gpt-4o-mini), get_openai_client(), call_llm()
    datetime_utils.py
    inventory_utils.py
    matching_utils.py
    nutrition_utils.py
    profile_utils.py
    prompt_loader.py
    shelf_life_utils.py
    text_utils.py        clean_markdown() — strips markdown from LLM output
    tracer.py            AgentTrace — per-request trace of LLM calls, tools, intent
    unit_utils.py
    web_search.py
  prompts/
    classify.txt
    shelf_life.txt
    nutrition.txt
    low_stock.txt
    ingredient_extraction.txt
    recipe_suggestion.txt
  scripts/
    audit_meal_nutrition.py
    backfill_health_scores.py
    backfill_meal_nutrition.py
  config/
    settings.py
  main.py
  requirements.txt

frontend/
  src/
    App.jsx
    main.jsx
    pages/
      LandingPage.jsx
      Login.jsx
      Signup.jsx
      VerifyEmail.jsx
      GettingStarted.jsx
      Dashboard.jsx
      Inventory.jsx
      MealPlan.jsx
      Nutrition.jsx
      SmartRecipes.jsx
      Profile.jsx
    services/
      api.jsx
    components/
      NotificationsDropdown.jsx
  vite.config.js
  tailwind.config.js
  package.json
```
