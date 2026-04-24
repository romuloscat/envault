"""CLI tests for envault cascade commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.store import set_secret
from envault.cli_cascade import cascade_cmd

PASSWORD = "cli-test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def primary(tmp_path):
    p = tmp_path / "primary.vault"
    set_secret("ALPHA", "alpha-val", PASSWORD, vault_path=p)
    set_secret("SHARED", "primary-shared", PASSWORD, vault_path=p)
    return p


@pytest.fixture()
def fallback(tmp_path):
    p = tmp_path / "fallback.vault"
    set_secret("BETA", "beta-val", PASSWORD, vault_path=p)
    set_secret("SHARED", "fallback-shared", PASSWORD, vault_path=p)
    return p


def _opt(vault, password=PASSWORD):
    return ["--vault", str(vault), "--password", password]


def test_cascade_set_and_show(runner, primary, fallback):
    result = runner.invoke(
        cascade_cmd, ["set"] + _opt(primary) + [str(fallback)]
    )
    assert result.exit_code == 0
    assert "->" in result.output

    result = runner.invoke(cascade_cmd, ["show", "--vault", str(primary)])
    assert result.exit_code == 0
    assert str(fallback) in result.output


def test_cascade_set_nonexistent_fallback_fails(runner, primary, tmp_path):
    ghost = tmp_path / "ghost.vault"
    result = runner.invoke(
        cascade_cmd, ["set"] + _opt(primary) + [str(ghost)]
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cascade_show_empty(runner, primary):
    result = runner.invoke(cascade_cmd, ["show", "--vault", str(primary)])
    assert result.exit_code == 0
    assert "No cascade configured" in result.output


def test_cascade_clear(runner, primary, fallback):
    runner.invoke(cascade_cmd, ["set"] + _opt(primary) + [str(fallback)])
    result = runner.invoke(cascade_cmd, ["clear", "--vault", str(primary)])
    assert result.exit_code == 0
    assert "cleared" in result.output

    result = runner.invoke(cascade_cmd, ["show", "--vault", str(primary)])
    assert "No cascade configured" in result.output


def test_cascade_resolve_from_fallback(runner, primary, fallback):
    runner.invoke(cascade_cmd, ["set"] + _opt(primary) + [str(fallback)])
    result = runner.invoke(
        cascade_cmd, ["resolve"] + _opt(primary) + ["BETA"]
    )
    assert result.exit_code == 0
    assert "beta-val" in result.output


def test_cascade_resolve_primary_wins(runner, primary, fallback):
    runner.invoke(cascade_cmd, ["set"] + _opt(primary) + [str(fallback)])
    result = runner.invoke(
        cascade_cmd, ["resolve"] + _opt(primary) + ["SHARED"]
    )
    assert result.exit_code == 0
    assert "primary-shared" in result.output


def test_cascade_resolve_missing_key_fails(runner, primary, fallback):
    runner.invoke(cascade_cmd, ["set"] + _opt(primary) + [str(fallback)])
    result = runner.invoke(
        cascade_cmd, ["resolve"] + _opt(primary) + ["DOES_NOT_EXIST"]
    )
    assert result.exit_code != 0


def test_cascade_dump(runner, primary, fallback):
    runner.invoke(cascade_cmd, ["set"] + _opt(primary) + [str(fallback)])
    result = runner.invoke(cascade_cmd, ["dump"] + _opt(primary))
    assert result.exit_code == 0
    assert "ALPHA=alpha-val" in result.output
    assert "BETA=beta-val" in result.output
    assert "SHARED=primary-shared" in result.output
