"""
Unit tests for backend.catalog: get_locations, get_cuisines, filter_restaurants.
Requires data/zomato_cleaned.csv. Skipped if file is missing.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "zomato_cleaned.csv"


def _has_data():
    return DATA_FILE.exists()


@pytest.mark.skipif(not _has_data(), reason="data/zomato_cleaned.csv not found")
class TestCatalog:
    """Tests that require real zomato_cleaned.csv."""

    def test_get_locations_returns_list(self):
        from backend.catalog import get_locations
        locs = get_locations()
        assert isinstance(locs, list)
        assert len(locs) > 0
        assert all(isinstance(x, str) for x in locs)

    def test_get_cuisines_returns_list(self):
        from backend.catalog import get_cuisines
        cuisines = get_cuisines()
        assert isinstance(cuisines, list)
        assert len(cuisines) > 0
        assert all(isinstance(x, str) for x in cuisines)

    def test_filter_restaurants_empty_filters_returns_rows(self):
        from backend.catalog import filter_restaurants
        df = filter_restaurants(location="", cuisines=[], min_rating=0.0, limit=10)
        assert len(df) <= 10
        assert "name" in df.columns
        assert "location" in df.columns
        assert "cuisine" in df.columns
        assert "rating" in df.columns
        assert "cost_for_two" in df.columns

    def test_filter_restaurants_by_location(self):
        from backend.catalog import get_locations, filter_restaurants
        locs = get_locations()
        if locs:
            loc = locs[0]
            df = filter_restaurants(location=loc, cuisines=[], min_rating=0.0, limit=20)
            assert all(df["location"].str.contains(loc, case=False, na=False))

    def test_filter_restaurants_by_min_rating(self):
        from backend.catalog import filter_restaurants
        df = filter_restaurants(location="", cuisines=[], min_rating=4.0, limit=50)
        assert (df["rating"] >= 4.0).all()

    def test_filter_restaurants_limit_respected(self):
        from backend.catalog import filter_restaurants
        df = filter_restaurants(location="", cuisines=[], min_rating=0.0, limit=5)
        assert len(df) <= 5
