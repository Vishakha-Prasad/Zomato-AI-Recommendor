"""
Vercel entrypoint: exposes FastAPI app for serverless deployment.
Vercel serves static files from public/; API routes are handled here.
"""

from backend.main import app
