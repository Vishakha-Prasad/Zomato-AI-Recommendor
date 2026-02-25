# AI Restaurant Recommendation System — Multi-Step Implementation Plan

This document breaks the project into ordered steps. **Dataset: Kaggle Zomato dataset** (`rajeshrampure/zomato-dataset`) loaded via `kagglehub`. **AI: Groq LLM** (see `ARCHITECTURE_PLAN.md`).

---

## Step 1: Environment & Dataset Loading

**Goal:** Set up Python env and load the Zomato dataset as a pandas DataFrame.

**Tasks:**
- Create a virtual environment (optional but recommended).
- Install: `kagglehub[pandas-datasets]`, `pandas`.
- Configure Kaggle API credentials if running locally (see [Kaggle API](https://github.com/Kaggle/kaggle-api)).
- Run the data loader script to download and load the dataset; verify columns (e.g. name, location, cuisine, price, rating).
- Map dataset columns to our model: **Location**, **Cuisine**, **Price**, **Ratings**.

**Deliverable:** `data_pipeline/load_zomato_data.py` runs successfully and prints `df.head()`, columns, shape, and **preference column mapping** (Location, Cuisine, Price, Ratings).

**Status:** Implemented. See `data_pipeline/STEP1_README.md` for run instructions.

**Details:** Run from project root:
```bash
pip install -r requirements.txt
python data_pipeline/load_zomato_data.py
```
In `data_pipeline/load_zomato_data.py`, set `FILE_PATH` to the CSV filename in the dataset (e.g. `"zomato.csv"` or `"Zomato data.csv"`). If unsure, use `FILE_PATH = ""` and the script will try a download fallback and load the first CSV found.

---

## Step 2: Data Exploration & Cleaning

**Goal:** Understand and clean the Zomato data for recommendations.

**Tasks:**
- Load dataset (from Step 1); inspect shape, dtypes, nulls.
- Identify columns for: **location** (area/city), **cuisine**, **price** (tier or cost_for_two), **ratings**.
- Handle missing values and duplicates; normalize location/cuisine strings (strip, lowercase, standardize).
- Derive or map **price tier** (e.g. ₹ / ₹₹ / ₹₹₹) from cost or existing column.
- Optionally export a cleaned CSV/parquet for the backend.

**Deliverable:** Cleaned DataFrame (or saved file) with columns aligned to recommendation filters.

---

## Step 3: Backend Foundation (API + Restaurant Catalog)

**Goal:** Expose the cleaned data via a simple API and persist as the restaurant catalog.

**Tasks:**
- Choose backend stack (e.g. FastAPI or Express).
- Load cleaned Zomato data into memory or a DB (SQLite/PostgreSQL).
- Implement endpoints:
  - `GET /restaurants` (optional: list with basic filters).
  - `POST /recommendations` — accepts `{ location, cuisine, price, ratings }`, returns filtered list (no AI yet).
- Add CORS and basic request validation.

**Deliverable:** Backend running; recommendation endpoint returns restaurants filtered by the four preferences.

---

## Step 4: Auth & Login API

**Goal:** Secure login and session so only authenticated users can get recommendations.

**Tasks:**
- Implement auth (e.g. JWT or session cookies).
- Endpoints: `POST /auth/login`, optional `POST /auth/register`, `GET /auth/me`.
- Protect `POST /recommendations` with auth middleware.
- Store users (and hashed passwords) in DB.

**Deliverable:** Login/register working; recommendation endpoint requires valid token/session.

---

## Step 5: Login Page (Frontend)

**Goal:** Login UI with spices image as background.

**Tasks:**
- Create Login page route.
- Use **Image 1 (spices, top-down)** as full-width or hero background.
- Implement login form (email, password, Sign in); call `POST /auth/login`; on success redirect to Recommendation page; on error show message.
- Store token/session (e.g. in memory, cookie, or localStorage) and send with API requests.

**Deliverable:** User can log in and be redirected to the Recommendation page.

---

## Step 6: Recommendation Page Shell & Filters

**Goal:** Recommendation page with preference filters and layout for results.

**Tasks:**
- Create Recommendation page (protected route; redirect to Login if not authenticated).
- Add **preference panel**: Location, Cuisine, Price, Ratings (dropdowns/chips/sliders) bound to state.
- Use **Images 2, 3, 4** (Indian spread, burger/fries, cocktails) as section backgrounds or carousel.
- Add “Get recommendations” button; call `POST /recommendations` with current filters.
- Display results area (list/grid of restaurant cards: name, location, cuisine, price, rating).

**Deliverable:** User can set filters and see recommendation results from the backend (filter-based only).

---

## Step 7: AI Ranking Integration (Groq LLM)

**Goal:** Use **Groq LLM** to re-rank filtered results for better personalization.

**Tasks:**
- After filtering by location, cuisine, price, ratings, pass the result set (or a subset) to the Groq API.
- Call Groq LLM to re-rank by relevance to user preferences (and optionally diversity). Use `GROQ_API_KEY` in backend env.
- Return ordered list to the client; keep fallback to non-AI sort if Groq is unavailable.

**Deliverable:** Recommendations are ordered by Groq LLM; UX unchanged except improved relevance.

---

## Step 8: Polish & Deployment

**Goal:** Production-ready UX and deployment.

**Tasks:**
- Responsive layout for Login and Recommendation pages.
- Error states (network error, empty results, invalid filters).
- Optional: remember last filters (e.g. in localStorage or user preferences API).
- Deploy frontend and backend (e.g. Vercel + Railway, or single-server).
- Document how to run locally and set Kaggle credentials.

**Deliverable:** App deployable and runnable from README; dataset loaded via `data_pipeline/load_zomato_data.py`.

---

## Dependency Overview

| Step | Depends on |
|------|------------|
| 1    | — |
| 2    | 1 |
| 3    | 2 |
| 4    | — (can parallelize with 3) |
| 5    | 4 |
| 6    | 3, 4, 5 |
| 7    | 3, 6 |
| 8    | 5, 6, 7 |

---

## Dataset Reference

- **Source:** Kaggle — `rajeshrampure/zomato-dataset`
- **Load method:** `kagglehub` with `KaggleDatasetAdapter.PANDAS`
- **Script:** `data_pipeline/load_zomato_data.py` (set `file_path` to the CSV filename in the dataset)
- **Preference mapping:** Location, Cuisine, Price, Ratings → dataset columns (defined in Step 2 after exploration).
