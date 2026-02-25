"""
Unit tests for backend.groq_ranker. No real Groq API calls.
Uses pytest.
"""

import pytest

from phase_2_backend_api.backend.models import Restaurant
from phase_2_backend_api.backend import groq_ranker


# ── Fallback behavior (no valid API key) ───────────────────────────────────────

def test_rerank_empty_list_returns_empty():
    """rerank([]) should return []."""
    result = groq_ranker.rerank([], {})
    assert result == []


def test_rerank_without_valid_key_returns_input():
    """When GROQ_API_KEY is missing or placeholder, rerank returns input unchanged."""
    restaurants = [
        Restaurant(name="R1", location="L1", cuisine="C1", cost_for_two=500, rating=4.0),
        Restaurant(name="R2", location="L2", cuisine="C2", cost_for_two=800, rating=4.5),
    ]
    result = groq_ranker.rerank(restaurants, {"location": "", "cuisines": [], "min_rating": 0})
    # Without valid key, groq_ranker falls back to returning input
    assert len(result) == 2
    assert result[0].name == "R1"
    assert result[1].name == "R2"


def test_rerank_preserves_restaurant_fields():
    """rerank should preserve Restaurant fields when falling back."""
    r = Restaurant(name="Test", location="X", cuisine="Y", cost_for_two=600, rating=4.2)
    result = groq_ranker.rerank([r], {})
    assert len(result) == 1
    assert result[0].name == r.name
    assert result[0].location == r.location
    assert result[0].cuisine == r.cuisine
    assert result[0].cost_for_two == r.cost_for_two
    assert result[0].rating == r.rating
