"""
FastAPI application entry point.
Run from project root:
  python -m uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from phase_2_backend_api.backend.routers import auth as auth_router
from phase_2_backend_api.backend.routers import restaurants as restaurants_router

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


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(_request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Data file unavailable. Please try again later.", "error": str(exc)},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/paths")
def debug_paths():
    """Temporary: inspect filesystem paths on Vercel for debugging."""
    import glob
    from pathlib import Path as P

    main_file = P(__file__).resolve()
    project_root = main_file.parent.parent.parent
    cwd = P.cwd()

    # Check all candidate paths
    candidates = {
        "__file__": str(main_file),
        "project_root": str(project_root),
        "cwd": str(cwd),
        "vercel_env": os.getenv("VERCEL", "not set"),
    }

    # Search for CSV files
    search_paths = [
        str(project_root / "phase_1_data_pipeline" / "data"),
        str(cwd / "phase_1_data_pipeline" / "data"),
        str(cwd),
        "/var/task",
    ]

    found_files = {}
    for sp in search_paths:
        try:
            if os.path.exists(sp):
                found_files[sp] = os.listdir(sp)[:20]
            else:
                found_files[sp] = "DOES NOT EXIST"
        except Exception as e:
            found_files[sp] = f"ERROR: {e}"

    # Also try to find any CSV files anywhere
    csv_glob = []
    for pattern in ["/var/task/**/*.csv", str(project_root / "**" / "*.csv")]:
        try:
            csv_glob.extend(glob.glob(pattern, recursive=True)[:10])
        except Exception:
            pass

    return {
        "paths": candidates,
        "dir_contents": found_files,
        "csv_files_found": csv_glob[:20],
    }

# Serve frontend static files (local dev only; Vercel serves from public/)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "phase_3_frontend_app", "public")
if not os.getenv("VERCEL") and os.path.exists(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    static_path = os.path.join(frontend_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/")
    def read_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))
