"""
Tests for Step 2: data cleaning logic. No Kaggle or network required.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add data_pipeline to path so we can import clean_data
SCRIPTS = Path(__file__).resolve().parent.parent.parent / "phase_1_data_pipeline" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from clean_data import (
    MAX_RATING,
    MIN_RATING,
    OUT_COST_FOR_TWO,
    OUT_CUISINE,
    OUT_LOCATION,
    OUT_NAME,
    OUT_RATING,
    OUT_REVIEWS,
    clean_zomato_df,
)


@pytest.fixture
def column_mapping():
    """Mapping matching common Zomato-style column names."""
    return {
        "Name": "name",
        "Location": "address",
        "Cuisine": "cuisines",
        "Price": "average_cost",
        "Ratings": "rating",
    }


@pytest.fixture
def raw_df():
    """Small raw DataFrame resembling Zomato data."""
    return pd.DataFrame({
        "name": ["Resto A", "Resto B", "Resto C", "Resto A", "Resto D"],
        "address": ["  MG Road  ", "Jayanagar", "Koramangala", "  MG Road  ", ""],
        "cuisines": ["North Indian, Chinese", "South Indian", "Cafe", None, "Fast Food"],
        "average_cost": [300, 600, 1200, 300, 500],
        "rating": [4.2, 4.5, 3.8, 4.2, None],
    })


def test_clean_zomato_df_has_required_columns(raw_df, column_mapping):
    """Cleaned DataFrame must have name, location, cuisine, cost_for_two, rating, reviews."""
    out = clean_zomato_df(raw_df, column_mapping)
    for col in (OUT_NAME, OUT_LOCATION, OUT_CUISINE, OUT_COST_FOR_TWO, OUT_RATING, OUT_REVIEWS):
        assert col in out.columns, f"Missing column {col}"


def test_clean_zomato_df_no_duplicates(raw_df, column_mapping):
    """Cleaned DataFrame should drop duplicate (name, location, cuisine)."""
    out = clean_zomato_df(raw_df, column_mapping)
    dupes = out.duplicated(subset=[OUT_NAME, OUT_LOCATION, OUT_CUISINE])
    assert not dupes.any(), "Duplicates should be removed"


def test_clean_zomato_df_cost_for_two_valid(raw_df, column_mapping):
    """cost_for_two must be numeric and non-negative."""
    out = clean_zomato_df(raw_df, column_mapping)
    assert (out[OUT_COST_FOR_TWO] >= 0).all(), "cost_for_two should be non-negative"
    assert out[OUT_COST_FOR_TWO].dtype in ("int64", "float64", "int32"), "cost_for_two should be numeric"


def test_clean_zomato_df_rating_in_range(raw_df, column_mapping):
    """Ratings must be between MIN_RATING and MAX_RATING."""
    out = clean_zomato_df(raw_df, column_mapping)
    assert (out[OUT_RATING] >= MIN_RATING).all() and (out[OUT_RATING] <= MAX_RATING).all()


def test_clean_zomato_df_no_nulls_in_rating(raw_df, column_mapping):
    """Rows with null rating are dropped."""
    out = clean_zomato_df(raw_df, column_mapping)
    assert out[OUT_RATING].notna().all()


def test_clean_zomato_df_location_normalized(raw_df, column_mapping):
    """Location should be stripped and lowercased."""
    out = clean_zomato_df(raw_df, column_mapping)
    row_a = out[out[OUT_NAME] == "Resto A"].iloc[0]
    assert row_a[OUT_LOCATION] == "mg road"


def test_clean_zomato_df_cuisine_first_only(raw_df, column_mapping):
    """Cuisine should take first of comma-separated list."""
    out = clean_zomato_df(raw_df, column_mapping)
    row_a = out[out[OUT_NAME] == "Resto A"].iloc[0]
    assert row_a[OUT_CUISINE] == "north indian"


def test_clean_zomato_df_cost_mapped(raw_df, column_mapping):
    """Numeric cost from Price column should be preserved in cost_for_two."""
    out = clean_zomato_df(raw_df, column_mapping)
    def get_cost(name):
        rows = out[out[OUT_NAME] == name]
        return rows[OUT_COST_FOR_TWO].iloc[0] if not rows.empty else None

    assert get_cost("Resto A") == 300
    assert get_cost("Resto B") == 600
    assert get_cost("Resto C") == 1200


def test_clean_zomato_df_drops_null_rating_rows(raw_df, column_mapping):
    """Resto D has null rating -> should be dropped."""
    out = clean_zomato_df(raw_df, column_mapping)
    assert "Resto D" not in out[OUT_NAME].values or out[out[OUT_NAME] == "Resto D"].empty


def test_clean_zomato_df_empty_mapping():
    """Empty or no matching columns returns empty DataFrame with correct columns."""
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    out = clean_zomato_df(df, {"Location": None, "Cuisine": None, "Price": None, "Ratings": None})
    assert out.shape[0] == 0
    for col in (OUT_NAME, OUT_LOCATION, OUT_CUISINE, OUT_COST_FOR_TWO, OUT_RATING, OUT_REVIEWS):
        assert col in out.columns


def test_clean_zomato_df_partial_mapping():
    """Only Location and Rating mapped still produces valid output."""
    df = pd.DataFrame({
        "address": ["Area1", "Area2"],
        "rating": [4.0, 3.5],
    })
    mapping = {"Name": None, "Location": "address", "Cuisine": None, "Price": None, "Ratings": "rating"}
    out = clean_zomato_df(df, mapping)
    # Cuisine can be NA; we drop only when BOTH location empty AND cuisine NA, and when rating NA
    assert out.shape[0] == 2
    assert list(out[OUT_LOCATION]) == ["area1", "area2"]
    assert list(out[OUT_RATING]) == [4.0, 3.5]
