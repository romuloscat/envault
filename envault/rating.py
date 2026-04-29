"""Secret rating/quality scoring for envault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

MIN_RATING = 1
MAX_RATING = 5


class RatingError(Exception):
    """Raised for invalid rating operations."""


def _rating_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".ratings.json")


def _load_ratings(vault_path: str) -> Dict[str, int]:
    path = _rating_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_ratings(vault_path: str, data: Dict[str, int]) -> None:
    _rating_path(vault_path).write_text(json.dumps(data, indent=2))


def set_rating(vault_path: str, key: str, rating: int) -> None:
    """Assign a quality rating (1–5) to a secret key."""
    if not (MIN_RATING <= rating <= MAX_RATING):
        raise RatingError(
            f"Rating must be between {MIN_RATING} and {MAX_RATING}, got {rating}."
        )
    data = _load_ratings(vault_path)
    data[key] = rating
    _save_ratings(vault_path, data)


def get_rating(vault_path: str, key: str) -> Optional[int]:
    """Return the rating for *key*, or None if not rated."""
    return _load_ratings(vault_path).get(key)


def remove_rating(vault_path: str, key: str) -> None:
    """Remove the rating for *key*."""
    data = _load_ratings(vault_path)
    if key not in data:
        raise RatingError(f"No rating found for key '{key}'.")
    del data[key]
    _save_ratings(vault_path, data)


def list_ratings(vault_path: str) -> Dict[str, int]:
    """Return all key→rating mappings, sorted by key."""
    data = _load_ratings(vault_path)
    return dict(sorted(data.items()))


def top_rated(vault_path: str, n: int = 5) -> Dict[str, int]:
    """Return the top-*n* highest-rated secrets."""
    data = _load_ratings(vault_path)
    sorted_items = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    return dict(sorted_items[:n])
