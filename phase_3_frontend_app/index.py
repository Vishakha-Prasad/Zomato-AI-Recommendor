"""
Vercel entrypoint: exposes FastAPI app for serverless deployment.
Vercel serves static files from public/; API routes are handled here.
Ensures project root is in sys.path for Vercel serverless.
On import failure, returns error details for debugging.
"""

import os
import sys
import traceback
from pathlib import Path

# Ensure project root is in sys.path (Vercel may run from different cwd)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Ensure cwd is project root for data file resolution
try:
    os.chdir(_root)
except OSError:
    pass

try:
    from phase_2_backend_api.backend.main import app

    # Temporary debug endpoint to inspect Vercel filesystem
    @app.get("/debug/paths")
    def debug_paths():
        import glob
        main_file = Path(__file__).resolve()
        project_root = main_file.parent.parent
        cwd = Path.cwd()
        candidates = {
            "index_py__file__": str(main_file),
            "project_root": str(project_root),
            "cwd": str(cwd),
            "vercel_env": os.getenv("VERCEL", "not set"),
        }
        search_paths = [
            str(project_root / "phase_1_data_pipeline" / "data"),
            str(cwd / "phase_1_data_pipeline" / "data"),
            str(cwd),
            "/var/task",
        ]
        found = {}
        for sp in search_paths:
            try:
                if os.path.exists(sp):
                    found[sp] = os.listdir(sp)[:20]
                else:
                    found[sp] = "NOT_FOUND"
            except Exception as ex:
                found[sp] = str(ex)
        csv_files = []
        for p in ["/var/task/**/*.csv", str(project_root / "**" / "*.csv")]:
            try:
                csv_files.extend(glob.glob(p, recursive=True)[:10])
            except Exception:
                pass
        return {"paths": candidates, "dirs": found, "csvs": csv_files[:20]}

except Exception as e:
    # Surface import/runtime errors for debugging (Vercel 500 crash)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def _error_handler(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            },
        )
