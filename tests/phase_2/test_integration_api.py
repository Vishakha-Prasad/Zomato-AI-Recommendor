"""
Integration tests that call real APIs (Kaggle, Groq). Skipped if credentials are missing.
Load .env before running so GROQ_API_KEY and KAGGLE_* are set.
Run: pytest tests/test_integration_api.py -v
"""

import os
import sys
from pathlib import Path

import pytest

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_env_file = PROJECT_ROOT / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

SCRIPTS = PROJECT_ROOT / "phase_1_data_pipeline" / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Check for Kaggle credentials (env or ~/.kaggle/kaggle.json)
def _has_kaggle_creds():
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        return True
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return kaggle_json.exists()


def _has_groq_creds():
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key) and not key.startswith("your_")


@pytest.mark.skipif(not _has_kaggle_creds(), reason="Kaggle credentials not set (KAGGLE_USERNAME/KAGGLE_KEY or ~/.kaggle/kaggle.json)")
def test_kaggle_load_and_clean():
    """Load real Zomato dataset from Kaggle and run cleaning. Requires Kaggle API."""
    from load_zomato_data import get_preference_mapping, load_via_download
    from clean_data import clean_zomato_df

    try:
        df = load_via_download()
    except Exception as e:
        pytest.skip(f"Could not download Kaggle dataset: {e}")

    mapping = get_preference_mapping(df)
    cleaned = clean_zomato_df(df, mapping)
    assert cleaned.shape[0] > 0, "Cleaned DataFrame should have rows"
    assert "location" in cleaned.columns and "rating" in cleaned.columns


@pytest.mark.skipif(not _has_groq_creds(), reason="GROQ_API_KEY not set in .env (or still placeholder)")
def test_groq_api_reachable():
    """Verify Groq API key works with a minimal completion. Requires GROQ_API_KEY in .env."""
    try:
        from groq import Groq
    except ImportError:
        pytest.skip("Install groq: pip install groq")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Reply with only the word OK."}],
        model="llama-3.3-70b-versatile",
        max_tokens=10,
    )
    text = (completion.choices[0].message.content or "").strip()
    assert len(text) > 0, "Groq should return a non-empty response"
