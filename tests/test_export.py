"""Tests for envault.export module."""

import json
import pytest

from envault.export import export_secrets, SUPPORTED_FORMATS


SAMPLE = {"DB_URL": "postgres://localhost/db", "SECRET_KEY": "s3cr3t", "PORT": "5432"}


def test_dotenv_format_contains_all_keys():
    out = export_secrets(SAMPLE, fmt="dotenv")
    for key in SAMPLE:
        assert key in out


def test_dotenv_format_quoted_values():
    out = export_secrets(SAMPLE, fmt="dotenv")
    assert 'DB_URL="postgres://localhost/db"' in out


def test_dotenv_escapes_double_quotes():
    out = export_secrets({"MSG": 'say "hello"'}, fmt="dotenv")
    assert 'MSG="say \\"hello\\""' in out


def test_bash_format_has_export():
    out = export_secrets(SAMPLE, fmt="bash")
    assert out.startswith("#!/usr/bin/env bash")
    for key in SAMPLE:
        assert f"export {key}=" in out


def test_bash_escapes_single_quotes():
    out = export_secrets({"VAR": "it's alive"}, fmt="bash")
    assert "it'\"'\"'s alive" in out


def test_json_format_is_valid_json():
    out = export_secrets(SAMPLE, fmt="json")
    parsed = json.loads(out)
    assert parsed == SAMPLE


def test_json_format_sorted_keys():
    out = export_secrets(SAMPLE, fmt="json")
    parsed = json.loads(out)
    assert list(parsed.keys()) == sorted(SAMPLE.keys())


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_secrets(SAMPLE, fmt="xml")


def test_empty_secrets_dotenv():
    assert export_secrets({}, fmt="dotenv") == ""


def test_empty_secrets_json():
    assert json.loads(export_secrets({}, fmt="json")) == {}
