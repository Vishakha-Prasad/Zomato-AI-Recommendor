"""
Groq LLM re-ranker for restaurant recommendations.
Falls back to rating-sorted list if GROQ_API_KEY is missing or call fails.
"""

from __future__ import annotations
import json
import os
from typing import Any

from backend.models import Restaurant

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"
MAX_RESTAURANTS_FOR_LLM = 20  # send at most this many to the LLM


def _has_valid_key() -> bool:
    key = GROQ_API_KEY.strip()
    return bool(key) and not key.startswith("your_")


def rerank(
    restaurants: list[Restaurant],
    preferences: dict[str, Any],
) -> list[Restaurant]:
    """
    Re-rank restaurants using Groq LLM.
    Falls back to the original (rating-sorted) order on any error.
    """
    if not restaurants:
        return restaurants

    if not _has_valid_key():
        return restaurants  # fallback: already sorted by rating

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY.strip())

        candidates = restaurants[:MAX_RESTAURANTS_FOR_LLM]
        numbered = "\n".join(
            f"{i+1}. {r.name} | {r.cuisine} | {r.price_tier} | rating {r.rating} | {r.location}"
            for i, r in enumerate(candidates)
        )
        prompt = (
            f"You are a restaurant recommendation assistant. "
            f"The user wants: location='{preferences.get('location', 'any')}', "
            f"cuisine='{preferences.get('cuisine', 'any')}', "
            f"price='{preferences.get('price_tier', 'any')}', "
            f"min_rating={preferences.get('min_rating', 0)}.\n\n"
            f"Here are the candidate restaurants (numbered):\n{numbered}\n\n"
            f"Return ONLY a JSON array of the numbers in your recommended order, "
            f"most relevant first. Example: [3,1,5,2,4]. No explanation."
        )

        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
            max_tokens=200,
            temperature=0.3,
        )
        raw = (completion.choices[0].message.content or "").strip()
        # Parse the number array
        order: list[int] = json.loads(raw)

        reranked: list[Restaurant] = []
        seen = set()
        for idx in order:
            if 1 <= idx <= len(candidates) and idx not in seen:
                reranked.append(candidates[idx - 1])
                seen.add(idx)
        # Append any not mentioned by LLM
        for i, r in enumerate(candidates, start=1):
            if i not in seen:
                reranked.append(r)
        # Append remaining restaurants beyond LLM window
        reranked.extend(restaurants[MAX_RESTAURANTS_FOR_LLM:])
        return reranked

    except Exception:
        return restaurants  # fallback on any error
