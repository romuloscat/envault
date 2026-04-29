"""Tests for envault.rating."""
import pytest
from pathlib import Path

from envault.rating import (
    RatingError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
    top_rated,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "vault.enc")


def test_set_and_get_rating(vault_file):
    set_rating(vault_file, "API_KEY", 4)
    assert get_rating(vault_file, "API_KEY") == 4


def test_get_rating_missing_key_returns_none(vault_file):
    assert get_rating(vault_file, "MISSING") is None


def test_set_rating_overwrites(vault_file):
    set_rating(vault_file, "DB_PASS", 3)
    set_rating(vault_file, "DB_PASS", 5)
    assert get_rating(vault_file, "DB_PASS") == 5


def test_set_rating_below_min_raises(vault_file):
    with pytest.raises(RatingError, match="between 1 and 5"):
        set_rating(vault_file, "KEY", 0)


def test_set_rating_above_max_raises(vault_file):
    with pytest.raises(RatingError, match="between 1 and 5"):
        set_rating(vault_file, "KEY", 6)


def test_set_rating_boundary_values(vault_file):
    set_rating(vault_file, "LOW", 1)
    set_rating(vault_file, "HIGH", 5)
    assert get_rating(vault_file, "LOW") == 1
    assert get_rating(vault_file, "HIGH") == 5


def test_remove_rating(vault_file):
    set_rating(vault_file, "TOKEN", 2)
    remove_rating(vault_file, "TOKEN")
    assert get_rating(vault_file, "TOKEN") is None


def test_remove_missing_rating_raises(vault_file):
    with pytest.raises(RatingError, match="No rating found"):
        remove_rating(vault_file, "GHOST")


def test_list_ratings_empty_when_none(vault_file):
    assert list_ratings(vault_file) == {}


def test_list_ratings_sorted_by_key(vault_file):
    set_rating(vault_file, "Z_KEY", 3)
    set_rating(vault_file, "A_KEY", 5)
    set_rating(vault_file, "M_KEY", 1)
    keys = list(list_ratings(vault_file).keys())
    assert keys == sorted(keys)


def test_top_rated_returns_highest(vault_file):
    set_rating(vault_file, "A", 5)
    set_rating(vault_file, "B", 3)
    set_rating(vault_file, "C", 4)
    set_rating(vault_file, "D", 1)
    result = top_rated(vault_file, n=2)
    assert list(result.keys()) == ["A", "C"]


def test_top_rated_n_larger_than_data(vault_file):
    set_rating(vault_file, "ONLY", 3)
    result = top_rated(vault_file, n=10)
    assert len(result) == 1
