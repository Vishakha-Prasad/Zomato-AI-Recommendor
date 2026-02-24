"""
FastAPI application entry point.
Run from project root:
  python -m uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.routers import auth as auth_router
from backend.routers import restaurants as restaurants_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Zomato Recommender API",
    description="AI-powered restaurant recommendations using the Zomato dataset and Groq LLM.",
    version="1.0.0",
)

# CORS — allow potential local development or cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(restaurants_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}

# Serve frontend static files
# Note: frontend directory must exist
frontend_path = os.path.join(os.getcwd(), "frontend")
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path)

app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))
