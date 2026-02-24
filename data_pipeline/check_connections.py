"""
Verify that phases (Steps 1 & 2) are connected and working. No Kaggle/network required.
Requires: pandas. Run from project root: python scripts/check_connections.py
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def main():
    errors = []
    step1_ok = False
    # 1) Step 1 module (optional: needs kagglehub; we can still verify Step 2 with manual mapping)
    get_preference_mapping = None
    try:
        from load_zomato_data import get_preference_mapping
        step1_ok = True
    except Exception:
        pass  # use manual mapping below if Step 1 not available

    # 2) Step 2 cleaning module
    try:
        from clean_data import (
            clean_zomato_df,
            OUT_LOCATION,
            OUT_CUISINE,
            OUT_PRICE_TIER,
            OUT_RATING,
            OUT_NAME,
        )
    except Exception as e:
        errors.append(f"Step 2 (clean_data): {e}")
        return errors

    # 3) Pipeline: synthetic data -> mapping -> clean -> standard columns
    import pandas as pd
    raw = pd.DataFrame({
        "name": ["Test Resto"],
        "address": ["MG Road"],
        "cuisines": ["Indian"],
        "average_cost": [500],
        "rating": [4.0],
    })
    mapping = (
        get_preference_mapping(raw)
        if get_preference_mapping is not None
        else {"Name": "name", "Location": "address", "Cuisine": "cuisines", "Price": "average_cost", "Ratings": "rating"}
    )
    cleaned = clean_zomato_df(raw, mapping)
    required_cols = {OUT_NAME, OUT_LOCATION, OUT_CUISINE, OUT_PRICE_TIER, OUT_RATING}
    if required_cols - set(cleaned.columns):
        errors.append(f"Step 2 output missing columns: {required_cols - set(cleaned.columns)}")
    if cleaned.shape[0] != 1:
        errors.append(f"Step 2 expected 1 row, got {cleaned.shape[0]}")

    # 4) .env and data/
    env_path = os.path.join(PROJECT_ROOT, ".env")
    data_dir = os.path.join(PROJECT_ROOT, "data")
    if not os.path.exists(env_path):
        errors.append(".env not found in project root")
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.isdir(data_dir):
        errors.append("data/ directory could not be created")

    return errors


if __name__ == "__main__":
    # Re-check if Step 1 is importable at module level for the summary message
    _step1_available = False
    try:
        from load_zomato_data import get_preference_mapping as _gpm
        _step1_available = True
    except Exception:
        pass

    errs = main()
    if errs:
        print("FAILED:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    msg = "OK: Step 2 (clean_data) and pipeline verified; .env and data/ present."
    if not _step1_available:
        msg += " (Step 1 load_zomato_data not importable; install kagglehub for full pipeline.)"
    else:
        msg += " Step 1 <-> Step 2 connected."
    print(msg)
