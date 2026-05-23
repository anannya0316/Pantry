# Pantry

**An AI-powered kitchen assistant that manages your pantry, plans your meals, and helps you eat better — all through a conversational interface.**

**Live demo: [frontend-pantry.vercel.app](https://frontend-pantry.vercel.app)**

Pantry connects your fridge to a multi-agent AI system. Tell it what you bought, ask it what you can cook tonight, log what you ate, and let it keep track of the rest — expiry dates, low stock, nutrition, weekly restocks.

---

## Features

**Inventory Management**
- Add ingredients with quantity, unit, and category (LLM-classified on input)
- Automatic shelf-life estimation per item
- Expiry tracking with notifications for items going stale
- Fuzzy-matched deduplication — "tomatoes" and "tomato" resolve to the same item

**Meal Planning**
- Build a weekly meal schedule (breakfast / lunch / dinner)
- LLM-powered ingredient extraction per meal, matched against current inventory
- Auto-consume: past meals automatically deduct ingredients from inventory
- Weekly restock: inventory quantities restored each new week from planned meals

**Nutrition Tracking**
- Log meals with a single message to the chatbot
- LLM-estimated macros and micros per serving (calories, protein, carbs, fat, fiber, vitamins)
- Health score per meal relative to the user's goals
- Weekly nutrition insights against daily targets

**Recipe Suggestions**
- Ask the chatbot for recipe ideas — it looks at what you actually have
- Returns structured recipes: ingredients, steps, have vs. need-to-buy breakdown

**Smart Shopping List**
- Deterministic rule-based list: out-of-stock + expired + low-stock items + missing meal-plan ingredients
- Scales quantities by household size
- Downloadable as a plain-text file

**Notifications**
- Expiring items, out-of-stock alerts, meal plan gaps, nutrition logging reminders

**Auth**
- Email + verification flow
- Google OAuth

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, TailwindCSS 4 |
| Backend | Python, FastAPI, Uvicorn |
| Database | MongoDB (PyMongo) |
| AI — Agent | LangGraph, LangChain, OpenRouter (`deepseek-v4-flash`) |
| AI — Utilities | OpenRouter (`gpt-4o-mini`) via OpenAI-compatible API |
| Fuzzy Matching | rapidfuzz |
| Web Search | Tavily (ingredient/classification fallback) |
| Auth | Google OAuth (`google-auth`), email verification |
| Background Jobs | FastAPI BackgroundTasks, APScheduler |
| Testing | pytest |

---

## Architecture

### Multi-Agent Chatbot (LangGraph)

The chatbot is the core of the product. Rather than a single LLM loop trying to do everything, it uses a **supervisor + specialist** architecture built on LangGraph:

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

Each specialist runs its own ReAct loop with a focused system prompt and a scoped tool set. Tools are created per-request via factory closures that capture `user_id`, so there's no global state.

Conversation history is persisted across requests via LangGraph's `MemorySaver`, keyed by `chat_id`.

### Backend Layers

```
Routes → Services → DAOs → MongoDB
            │
            ├── LLM calls (classification, nutrition, shelf life, ingredients)
            ├── Fuzzy matching (rapidfuzz) for ingredient resolution
            └── Background tasks (shelf life fetch, nutrition logging)
```

Services are stateless. DAOs handle all MongoDB access. The chatbot tools call services directly, so the same business logic powers both the REST API and the chatbot.

---

## Project Structure

```
backend/
├── api/routes/          REST endpoints (auth, inventory, meal plan, nutrition, profile…)
├── chatbot/
│   ├── agent.py         LangGraph supervisor + 6 specialist subagents
│   ├── tools/           Tool implementations (inventory, meal_plan, nutrition, profile, recipes, shopping)
│   ├── evals/           Eval suite for chatbot tool correctness
│   └── tests/           Unit tests
├── services/            Business logic (classification, nutrition, meal, shelf life, auth…)
├── dao/                 MongoDB data access layer
├── models/              Pydantic request/response models
├── utils/               LLM client, fuzzy matching, prompt loader, tracer, datetime utils
└── prompts/             LLM prompt templates

frontend/
└── src/
    ├── pages/           Dashboard, Inventory, MealPlan, Nutrition, SmartRecipes, Profile…
    ├── services/        API client (Axios)
    └── components/      NotificationsDropdown
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- OpenRouter API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Fill in: MONGO_URI, OPEN_ROUTER_KEY, GOOGLE_CLIENT_ID, EMAIL_*, etc.

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### Environment Variables

**Backend (`backend/.env`)**

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | MongoDB Atlas connection string |
| `OPEN_ROUTER_KEY` | OpenRouter API key (agent + all utility LLM calls) |
| `TAVILY_API_KEY` | Tavily search API key (optional — fallback for classification) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL` | SMTP config for verification emails |
| `FRONTEND_BASE_URL` | Frontend URL — used in email verification links |

**Frontend (`frontend/.env`)**

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (falls back to `http://localhost:8000` locally) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

---

## API Overview

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/create-account`, `/auth/login`, `/auth/verify-email`, `/auth/google` |
| Profile | `GET /profile/`, `PUT /profile/update`, `GET /profile/insights` |
| Inventory | `GET /inventory/`, `POST /inventory/add`, `PUT /inventory/update`, `GET /inventory/low-stock` |
| Meal Plan | `GET /meal-plan/`, `POST /meal-plan/add`, `POST /meal-plan/delete` |
| Nutrition | `POST /nutrition/log-recipe`, `GET /nutrition/insights` |
| Chatbot | `POST /recipes/suggest`, `GET /recipes/shopping-list/download` |
| Notifications | `GET /notifications/` |

All authenticated endpoints read the user identity from a `user-id` request header.

---

## Deployment

Both frontend and backend are deployed on Vercel as separate projects. The agent is stateless — conversation history is owned by the client and sent with each request, so there's no server-side session state.

| Part | Platform | URL |
|------|----------|-----|
| Frontend | [Vercel](https://vercel.com) | `your-app.vercel.app` |
| Backend | [Vercel](https://vercel.com) | `your-backend.vercel.app` |
| Database | [MongoDB Atlas](https://www.mongodb.com/atlas) M0 | connection string only |

### Deploy the backend

1. Push your repo to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → import your repo
3. Click the **backend** service card, set **Root Directory** to `backend`
4. Add environment variables from `backend/.env.example`
5. Deploy — copy the generated URL

### Deploy the frontend

1. New Project → import the same repo → click the **frontend** service card
2. Root Directory: `frontend`
3. Add environment variables:
   - `VITE_API_URL` → your backend Vercel URL
   - `VITE_GOOGLE_CLIENT_ID` → your Google OAuth client ID
4. Deploy → get the frontend URL
5. Go back to the backend project → add `FRONTEND_BASE_URL` = your frontend URL → redeploy

### After deploying

- **Google OAuth**: add your frontend URL to **Authorised JavaScript origins** in [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials

---

## Design Decisions

**Supervisor routing over intent classification + single loop.** A structured-output supervisor that picks one of six agents is simpler to debug and extend than a single loop that classifies intent and then re-routes internally. Each agent has a narrow contract.

**Rule-based shopping list.** The shopping list has no LLM call — it's a deterministic rule engine (thresholds per unit, meal-plan ingredient cross-check). LLM calls are reserved for things that actually need language understanding.

**Fuzzy matching everywhere.** Ingredient names are messy. `rapidfuzz` runs on every inventory lookup so "capsicum" finds "bell pepper" and "tomatos" finds "tomatoes" without requiring exact strings.

**Background tasks for slow LLM calls.** Shelf-life estimation and nutrition fetch after adding a meal are dispatched as background tasks so the user's request returns immediately.

**Inventory items are never deleted.** Items are quantity-deducted or marked consumed. This preserves history and avoids race conditions on concurrent updates.
