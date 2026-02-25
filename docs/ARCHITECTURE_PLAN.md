# AI Restaurant Recommendation System — Architecture Plan

**Document version:** 1.1  
**Role:** Product / Architecture  
**Last updated:** February 2025  

**AI / Ranking:** This system uses **Groq LLM** for re-ranking restaurant recommendations (see §5, §8, §11).

---

## 1. Executive Summary

This document defines the architecture for an **AI Restaurant Recommendation System** that lets users log in and receive personalized restaurant suggestions based on **Location**, **Cuisine**, **Price**, and **Ratings**. The system has two main surfaces: a **Login** page and a **Recommendation** page, with clear separation of auth, preferences, and recommendation logic.

---

## 2. Product Goals & Scope

| Goal | Description |
|------|-------------|
| **Personalization** | Use AI to rank and recommend restaurants from user preferences. |
| **Trust & identity** | Secure login so preferences and history can be tied to a user. |
| **Clarity** | Simple filters: Location, Cuisine, Price, Ratings. |
| **Engagement** | Strong visual design using provided imagery on Login and Recommendation pages. |

**Out of scope (v1):** Payments, table booking, reviews submission, multi-language.

---

## 3. User Flows

### 3.1 Login Flow

1. User lands on **Login** page (background: spices imagery).
2. User enters credentials (e.g. email + password) or uses OAuth if supported.
3. System validates and creates session; redirect to **Recommendation** page.
4. Invalid login: show error, stay on Login.

### 3.2 Recommendation Flow

1. User is on **Recommendation** page (authenticated).
2. User sets or adjusts preferences:
   - **Location** (e.g. city, area, or “current location”).
   - **Cuisine** (e.g. Indian, Fast food, Bar / Cocktails).
   - **Price** (e.g. ₹ / $ tiers or range).
   - **Ratings** (e.g. minimum rating or “highly rated”).
3. User triggers “Get recommendations” (or recommendations load automatically).
4. System (backend + AI) returns a ranked list of restaurants.
5. UI displays results (cards/list) with option to refine filters.

---

## 4. Page & Visual Design

### 4.1 Login Page

- **Purpose:** Authenticate user and establish session.
- **Background / hero:** Use **Image 1 — Spices (top-down)** as full-width or hero background.
  - Path: `assets/.../images_Zomato-58d34042-b9fa-42ab-969e-ff17b0c4a0a0.png` (or first image as per your asset list).
  - Dark, textured surface and open space (especially lower half) suit overlay of login form and branding.
- **UI elements:**
  - Centered or side-aligned login card (email, password, “Sign in”, “Forgot password?”, optional “Sign up”).
  - Logo / app name; optional tagline.
  - Keep form compact so the spices imagery remains visible.

### 4.2 Recommendation Page

- **Purpose:** Set preferences and view AI-powered restaurant recommendations.
- **Imagery:** Use **Images 2, 3, 4** to support the “Cuisine” and “experience” theme:
  - **Image 2 — Indian / South Asian spread:** Hero or section for “Indian / traditional” or “feast” vibe (`assets/.../indian-delicious-food-top-view_1174497-43921-2821ed2c-d8e4-4cab-a56e-77f6de6317df.png`).
  - **Image 3 — Burger & fries:** Section or carousel for “Fast food / casual” or “comfort food” (`assets/.../OIP-c4498fe8-50bf-4529-8bac-7bfaa42067b5.png`).
  - **Image 4 — Cocktails:** Section or carousel for “Bar / drinks / nightlife” or “premium” vibe (`assets/.../different-beautiful-cocktails-dark-background-bar-counter-...-f88879b6-2a3b-4863-80c2-ce18e59242c2.png`).
- **Layout:**
  - **Preference panel:** Location, Cuisine, Price, Ratings (dropdowns, sliders, or chips).
  - **Results area:** List or grid of restaurant cards (photo, name, cuisine, price, rating, CTA).
  - Optional: Rotating or section-based use of Images 2–4 (e.g. by selected cuisine or as category headers).

---

## 5. System Architecture (High Level)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Web App)                               │
│  ┌─────────────────┐  ┌─────────────────────────────────────────────┐   │
│  │   Login Page    │  │           Recommendation Page               │   │
│  │  (Image 1 BG)   │  │  Filters + Results (Images 2,3,4 as theme)  │   │
│  └────────┬────────┘  └───────────────────────┬─────────────────────┘   │
│           │                                   │                          │
│           │ Auth (token/session)              │ Preferences + Request   │
└───────────┼───────────────────────────────────┼──────────────────────────┘
            │                                   │
            ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY / BFF                                │
│              (Auth middleware, rate limit, routing)                      │
└───────────┬─────────────────────────────────┬───────────────────────────┘
            │                                 │
            ▼                                 ▼
┌───────────────────────┐     ┌──────────────────────────────────────────┐
│   Auth Service        │     │     Recommendation Service               │
│   - Login / Register  │     │  - Accept: location, cuisine, price,      │
│   - Session / JWT     │     │    ratings                                 │
│   - Password reset    │     │  - Call Groq LLM ranking + Restaurant catalog │
└───────────────────────┘     └──────────────────┬───────────────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                             ▼                             ▼
          ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
          │  Restaurant      │         │  Groq LLM        │         │  User           │
          │  Catalog / DB    │         │  Ranking Engine  │         │  Preferences DB │
          │  (Zomato dataset)│         │  (re-rank by     │         │  (optional)     │
          │                  │         │   preferences)   │         │                  │
          └─────────────────┘         └─────────────────┘         └─────────────────┘
```

- **Client:** Login page + Recommendation page; assets (images) referenced as above.
- **API layer:** Handles auth and recommendation requests.
- **Auth service:** Login, session/JWT, optional sign-up and password reset.
- **Recommendation service:** Takes Location, Cuisine, Price, Ratings; uses **Restaurant catalog** (Zomato dataset) and **Groq LLM** for ranking to return ordered list.
- **Optional:** User preferences store for “remember last filters” or learning over time.

---

## 6. Data Model (Core)

### 6.1 Preference Payload (Request)

| Field     | Type   | Description / Example                          |
|----------|--------|--------------------------------------------------|
| location | string | City, area, or geo (lat/lng)                     |
| cuisine  | string | e.g. "Indian", "Fast food", "Bar / Cocktails"   |
| price    | string | e.g. "₹", "₹₹", "₹₹₹" or 1–3 / low–high         |
| ratings  | number | Min rating (e.g. 4.0) or "highly rated" flag    |

### 6.2 Restaurant (Catalog / Response)

| Field      | Type   | Description                    |
|-----------|--------|--------------------------------|
| id        | string | Unique identifier              |
| name      | string | Restaurant name                |
| location  | string | Address / area                 |
| cuisine   | string | Primary cuisine                |
| priceTier | string | Price tier                     |
| rating    | number | Average rating                 |
| imageUrl  | string | Optional cover image           |

### 6.3 User (Auth)

| Field   | Type   | Description     |
|--------|--------|-----------------|
| id     | string | User ID         |
| email  | string | Login email     |
| ...    | ...    | Hashed password, profile fields as needed |

---

## 7. API Contract (Summary)

| Method | Endpoint            | Auth | Description                    |
|--------|---------------------|------|--------------------------------|
| POST   | /auth/login         | No   | Body: email, password → token |
| POST   | /auth/register      | No   | Body: email, password, ...    |
| GET    | /auth/me            | Yes  | Current user profile          |
| POST   | /recommendations    | Yes  | Body: location, cuisine, price, ratings → list of restaurants |
| GET    | /restaurants        | Yes  | Optional: list/catalog (filtered) |

---

## 8. AI Recommendation Logic (Groq LLM)

- **LLM:** **Groq** (https://groq.com). Use Groq’s API with a suitable model (e.g. `llama3-70b-8192` or current default) for fast inference. API key via `GROQ_API_KEY` environment variable.
- **Input:** location, cuisine, price, ratings (and optionally user id for future personalization).
- **Steps:**
  1. **Retrieval:** From restaurant catalog (Zomato dataset), filter by location and optionally cuisine/price/rating thresholds.
  2. **Ranking:** Call **Groq LLM** with the filtered list and user preferences; prompt the model to re-rank by fit to “Cuisine + Price + Ratings” and optionally diversity. Parse the model’s ordered list (e.g. by restaurant id or name).
  3. **Output:** Ordered list of restaurant objects (id, name, location, cuisine, priceTier, rating, imageUrl, etc.).
- **Fallback:** If Groq API is unavailable or errors, return deterministic sort (e.g. by rating, then price).

---

## 9. Security & Auth

- **Login:** Secure session or JWT; HTTPS only.
- **Passwords:** Hashed (e.g. bcrypt/argon2); never log or return.
- **Recommendation API:** Protected by auth middleware; reject unauthenticated requests.
- **Input validation:** Sanitize location, cuisine, price, ratings to avoid injection and bad data.

---

## 10. Asset Mapping (Implementation Reference)

| Usage              | Asset description        | Path (under project) |
|--------------------|--------------------------|----------------------|
| Login page background | Spices (top-down)     | `assets/c__Users_Vishakha_Prasad_AppData_Roaming_Cursor_User_workspaceStorage_afffcc418ec809000a2f2523e8c9b389_images_Zomato-58d34042-b9fa-42ab-969e-ff17b0c4a0a0.png` |
| Recommendation — Indian / feast | Indian dishes spread | `assets/c__Users_Vishakha_Prasad_AppData_Roaming_Cursor_User_workspaceStorage_afffcc418ec809000a2f2523e8c9b389_images_indian-delicious-food-top-view_1174497-43921-2821ed2c-d8e4-4cab-a56e-77f6de6317df.png` |
| Recommendation — Fast food     | Burger & fries        | `assets/c__Users_Vishakha_Prasad_AppData_Roaming_Cursor_User_workspaceStorage_afffcc418ec809000a2f2523e8c9b389_images_OIP-c4498fe8-50bf-4529-8bac-7bfaa42067b5.png` |
| Recommendation — Bar / drinks  | Cocktails             | `assets/c__Users_Vishakha_Prasad_AppData_Roaming_Cursor_User_workspaceStorage_afffcc418ec809000a2f2523e8c9b389_images_different-beautiful-cocktails-dark-background-bar-counter-3d-illustration-generative-ai_170984-4736-f88879b6-2a3b-4863-80c2-ce18e59242c2.png` |

Use these paths when implementing the Login and Recommendation pages so the correct visuals are applied.

---

## 11. Tech Stack (Suggested)

| Layer        | Option A              | Option B              |
|-------------|------------------------|------------------------|
| Frontend    | React + Vite           | Next.js (SSR/SSG)     |
| Styling     | Tailwind CSS / CSS modules | Same                  |
| Auth        | JWT + httpOnly cookie | NextAuth / Auth0       |
| Backend     | Node (Express/Fastify)| Python (FastAPI)       |
| **AI**      | **Groq LLM** (re-ranking; API key: `GROQ_API_KEY`) | — |
| Database    | PostgreSQL + Prisma   | MongoDB / Firebase     |
| Restaurant data | Zomato dataset (Kaggle) loaded into DB or in-memory | Same |

---

## 12. Project Structure (Target)

```
project-root/
├── docs/
│   ├── ARCHITECTURE_PLAN.md          # This document
│   ├── IMPLEMENTATION_STEPS.md       # Step-by-step guide
│   └── logs/                         # Agent transcripts and diagnostic logs
├── data_pipeline/                    # Python scripts for data loading/cleaning
├── mcp_servers/                      # MCP tools and server configurations
├── assets/
│   └── images/                       # Login + Recommendation images (1–4)
├── tests/                            # Integration and unit tests
├── src/                              # Frontend source code (future)
│   ├── app/                          # Routes / pages
│   └── components/                   # UI components
├── backend/                          # API backend (future)
│   ├── auth/
│   └── recommendations/
├── .env                              # Environment variables (GROQ_API_KEY, etc.)
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## 13. Implementation Phases

| Phase | Scope | Outcome |
|-------|--------|--------|
| **P1** | Auth + Login page with Image 1 | User can log in and be redirected |
| **P2** | Recommendation page shell + preference UI (Location, Cuisine, Price, Ratings) | Filters visible; mock or static results |
| **P3** | Backend recommendation API + restaurant catalog (seed or API) | Real data returned by filters |
| **P4** | AI ranking integration | Recommendations ordered by AI using preferences |
| **P5** | Polish: Images 2–4 on Recommendation page, responsive layout, error states | Production-ready UX |

---

## 14. Success Metrics (Recommendations)

- **Login:** Conversion (visit → successful login), time to login.
- **Recommendations:** Click-through on recommended restaurants, filter usage (which of Location/Cuisine/Price/Ratings is used most).
- **Engagement:** Return visits, number of recommendation requests per session.

---

## 15. Open Decisions

- Restaurant catalog: Zomato dataset (Kaggle) loaded in Step 1; persist in DB or in-memory per backend choice.
- **AI provider: Groq LLM** (decided); set `GROQ_API_KEY` in backend env.
- Whether to support “current location” (geo) in v1.
- OAuth providers (Google, Apple, etc.) for login.

---

*This architecture plan is the single source of truth for the AI Restaurant Recommendation System’s structure, flows, and use of the Login image (1) and Recommendation images (2, 3, 4).*
