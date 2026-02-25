"""
Vercel entrypoint: exposes FastAPI app for serverless deployment.
Vercel serves static files from public/; API routes are handled here.
Ensures project root is in sys.path for Vercel serverless.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path (Vercel may run from different cwd)
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Ensure cwd is project root for data file resolution
try:
    os.chdir(_root)
except OSError:
    pass

from backend.main import app
