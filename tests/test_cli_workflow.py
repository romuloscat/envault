"""Tests for envault.cli_workflow."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_workflow import workflow_cmd
from envault.store import set_secret

PASSWORD = "test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def _opt(vault_file):
    return ["--vault", vault_file]


def test_wf_set_and_list(runner, vault_file):
    result = runner.invoke(
        workflow_cmd, ["set"] + _opt(vault_file) + ["deploy", "DB_URL", "API_KEY"]
    )
    assert result.exit_code == 0
    assert "deploy" in result.output

    result = runner.invoke(workflow_cmd, ["list"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "deploy" in result.output


def test_wf_list_empty(runner, vault_file):
    result = runner.invoke(workflow_cmd, ["list"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_wf_show(runner, vault_file):
    runner.invoke(
        workflow_cmd, ["set"] + _opt(vault_file) + ["init", "SECRET_A", "SECRET_B"]
    )
    result = runner.invoke(workflow_cmd, ["show"] + _opt(vault_file) + ["init"])
    assert result.exit_code == 0
    assert "SECRET_A" in result.output
    assert "SECRET_B" in result.output


def test_wf_show_missing(runner, vault_file):
    result = runner.invoke(workflow_cmd, ["show"] + _opt(vault_file) + ["ghost"])
    assert result.exit_code != 0


def test_wf_remove(runner, vault_file):
    runner.invoke(
        workflow_cmd, ["set"] + _opt(vault_file) + ["deploy", "KEY"]
    )
    result = runner.invoke(workflow_cmd, ["remove"] + _opt(vault_file) + ["deploy"])
    assert result.exit_code == 0
    result = runner.invoke(workflow_cmd, ["list"] + _opt(vault_file))
    assert "deploy" not in result.output


def test_wf_validate_success(runner, vault_file):
    set_secret(vault_file, "DB_URL", "postgres://", PASSWORD)
    runner.invoke(
        workflow_cmd, ["set"] + _opt(vault_file) + ["deploy", "DB_URL"]
    )
    result = runner.invoke(
        workflow_cmd,
        ["validate", "--vault", vault_file, "--password", PASSWORD, "deploy"],
    )
    assert result.exit_code == 0
    assert "valid" in result.output


def test_wf_validate_failure(runner, vault_file):
    runner.invoke(
        workflow_cmd, ["set"] + _opt(vault_file) + ["deploy", "MISSING"]
    )
    result = runner.invoke(
        workflow_cmd,
        ["validate", "--vault", vault_file, "--password", PASSWORD, "deploy"],
    )
    assert result.exit_code != 0
    assert "MISSING" in result.output
