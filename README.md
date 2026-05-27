# Pantry

**Your AI-powered kitchen assistant — manage your pantry, plan meals, track nutrition, and get recipes, all through a conversational interface.**

**Live demo → [frontend-pantry.vercel.app](https://frontend-pantry.vercel.app)**

---

## What it does

Pantry connects your fridge to a multi-agent AI system. Tell it what you bought, ask what you can cook tonight, log what you ate — it keeps track of the rest. Expiry dates, low stock, weekly meal plans, nutrition, and grocery lists, all in one place.

The core is a **LangGraph supervisor + 6 specialist agents**. A supervisor LLM routes each message to the right specialist (inventory, meal plan, recipe, nutrition, etc.), which then runs its own ReAct loop with a focused tool set. The same business logic that powers the chatbot also drives the REST API, so every feature works both ways.

---

## Screenshots

### Dashboard
Get a snapshot of your pantry health — alignment to your goals, diet balance, food waste risk, and grocery efficiency.

![Dashboard](images/Screenshot%202026-05-27%20081015.png)

---

### Inventory
Track every item with quantity, category, expiry status, and purchase date. Items are fuzzy-matched on entry so "tomatoe" and "tomatoes" resolve to the same item.

![Inventory](images/Screenshot%202026-05-27%20072106.png)

---

### Meal Planning
Build a weekly meal schedule. Past meals auto-consume ingredients from your pantry. Every Monday, inventory is restocked based on the current plan.

![Meal Planning](images/Screenshot%202026-05-27%20072119.png)

---

### Nutrition Insights
Track macros, calories, health scores, and weekly trends. Health score is calculated per meal against your personal daily targets.

![Nutrition Insights](images/Screenshot%202026-05-27%20072135.png)

---

### AI Recipe Suggestions
Ask the chatbot for a recipe — it looks at what you actually have and returns a structured result with ingredients, steps, and a clear have vs. need-to-buy split.

![Recipe](images/Screenshot%202026-05-27%20090028.png)

---

### Shopping List
One message generates a prioritised shopping list: out-of-stock items, low-stock items, and ingredients missing for your planned meals. No LLM involved — fully rule-based so it never hallucinates.

![Shopping List](images/Screenshot%202026-05-27%20090232.png)

---

### Natural Language Profile Updates
Update your diet, goals, and preferences in plain English. The agent interprets and persists the changes.

![Profile Update](images/Screenshot%202026-05-27%20090939.png)

---

### Weekly Nutrition Summary
Ask how you've been eating this week. The agent combines your nutrition logs and consumed meal plan entries to give a full picture.

![Weekly Summary](images/Screenshot%202026-05-27%20091732.png)

---

## Architecture

```
User message
    │
    ▼
Supervisor (structured-output LLM)
    │  classifies intent →
    ├── inventory      ReAct agent  add/update/query pantry items
    ├── meal_plan      ReAct agent  view/add/reschedule weekly meals
    ├── profile        ReAct agent  update diet, goals, preferences
    ├── nutrition_log  ReAct agent  log meals, query nutrition history
    ├── recipe         ReAct agent  generate recipes from inventory
    └── shopping_list  ReAct agent  generate prioritised shopping list
```

Each specialist has a scoped system prompt and a set of tools created per-request via factory closures that capture `user_id`. Conversation history is persisted in-process via LangGraph `MemorySaver`.

```
Routes → Services → DAOs → MongoDB
            │
            ├── LLM calls (classification, nutrition, shelf life, ingredients)
            ├── Fuzzy matching (rapidfuzz) for ingredient resolution
            └── Background tasks (shelf life fetch, nutrition logging)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, TailwindCSS 4 |
| Backend | Python, FastAPI |
| Database | MongoDB (PyMongo) |
| AI — Agent | LangGraph, LangChain, OpenRouter (`deepseek-v4-flash`) |
| AI — Utilities | OpenRouter (`gpt-4o-mini`) — classification, nutrition, shelf life |
| Fuzzy Matching | rapidfuzz |
| Web Search | Tavily (fallback for classification & ingredient extraction) |
| Auth | Google OAuth, email verification |
| Background Jobs | FastAPI BackgroundTasks, APScheduler |

---

## Getting Started

### Prerequisites
- Python 3.11+, Node.js 18+, MongoDB, OpenRouter API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in MONGO_URI, OPEN_ROUTER_KEY, etc.
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### Environment Variables

**Backend (`backend/.env`)**

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | MongoDB Atlas connection string |
| `OPEN_ROUTER_KEY` | OpenRouter API key |
| `TAVILY_API_KEY` | Tavily search key (optional) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL` | Email verification |
| `FRONTEND_BASE_URL` | Frontend URL for email links |

**Frontend (`frontend/.env`)**

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (defaults to `http://localhost:8000`) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

---

## Design Decisions

**Supervisor routing over a single loop.** A structured-output supervisor picking one of six agents is simpler to debug and extend than a single model trying to classify intent and act at the same time. Each agent has a narrow contract.

**Rule-based shopping list.** The shopping list has no LLM call — it's a deterministic rule engine (thresholds per unit, meal-plan ingredient cross-check). LLM calls are reserved for things that actually need language understanding.

**Fuzzy matching everywhere.** Ingredient names are messy. `rapidfuzz` runs on every inventory lookup so "capsicum" finds "bell pepper" without requiring exact strings.

**Inventory items are never deleted.** Items are quantity-deducted or marked consumed. This preserves history and avoids race conditions on concurrent updates.

**Background tasks for slow LLM calls.** Shelf-life estimation and nutrition fetch run as background tasks so the user's request returns immediately.
