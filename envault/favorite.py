"""Manage favorite (starred) secrets for quick access."""

from __future__ import annotations

import json
from pathlib import Path


class FavoriteError(Exception):
    pass


def _favorite_path(vault_file: Path) -> Path:
    return vault_file.parent / (vault_file.stem + ".favorites.json")


def _load_favorites(vault_file: Path) -> list[str]:
    path = _favorite_path(vault_file)
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def _save_favorites(vault_file: Path, favorites: list[str]) -> None:
    path = _favorite_path(vault_file)
    with path.open("w") as f:
        json.dump(favorites, f, indent=2)


def add_favorite(vault_file: Path, key: str) -> None:
    favorites = _load_favorites(vault_file)
    if key not in favorites:
        favorites.append(key)
        _save_favorites(vault_file, favorites)


def remove_favorite(vault_file: Path, key: str) -> None:
    favorites = _load_favorites(vault_file)
    if key not in favorites:
        raise FavoriteError(f"Key '{key}' is not in favorites.")
    favorites.remove(key)
    _save_favorites(vault_file, favorites)


def list_favorites(vault_file: Path) -> list[str]:
    return _load_favorites(vault_file)


def is_favorite(vault_file: Path, key: str) -> bool:
    return key in _load_favorites(vault_file)
