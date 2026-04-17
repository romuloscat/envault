"""Tests for envault.lint."""
import pytest
from unittest.mock import patch
from envault.lint import lint_vault, LintIssue, LintError


VAULT = '/fake/vault'
PASS = 'pass'


def _patch(keys=None, expiry=None, expired=False, tags=None):
    keys = keys or []
    return (
        patch('envault.lint.list_secrets', return_value=keys),
        patch('envault.lint.get_expiry', return_value=expiry),
        patch('envault.lint.is_expired', return_value=expired),
        patch('envault.lint.get_tags', return_value=tags or []),
    )


def test_no_issues_for_clean_secret():
    with patch('envault.lint.list_secrets', return_value=['DB_HOST']), \
         patch('envault.lint.get_expiry', return_value=None), \
         patch('envault.lint.is_expired', return_value=False), \
         patch('envault.lint.get_tags', return_value=['prod']):
        issues = lint_vault(VAULT, PASS)
    assert issues == []


def test_warns_on_lowercase_key():
    with patch('envault.lint.list_secrets', return_value=['db_host']), \
         patch('envault.lint.get_expiry', return_value=None), \
         patch('envault.lint.is_expired', return_value=False), \
         patch('envault.lint.get_tags', return_value=['prod']):
        issues = lint_vault(VAULT, PASS)
    keys_msgs = [(i.key, i.message) for i in issues]
    assert any('UPPER_SNAKE_CASE' in m for _, m in keys_msgs)


def test_warns_on_weak_key_name():
    with patch('envault.lint.list_secrets', return_value=['PASSWORD']), \
         patch('envault.lint.get_expiry', return_value=None), \
         patch('envault.lint.is_expired', return_value=False), \
         patch('envault.lint.get_tags', return_value=['prod']):
        issues = lint_vault(VAULT, PASS)
    assert any('generic' in i.message for i in issues)


def test_error_on_expired_secret():
    with patch('envault.lint.list_secrets', return_value=['API_KEY']), \
         patch('envault.lint.get_expiry', return_value='2000-01-01T00:00:00'), \
         patch('envault.lint.is_expired', return_value=True), \
         patch('envault.lint.get_tags', return_value=['prod']):
        issues = lint_vault(VAULT, PASS)
    errors = [i for i in issues if i.level == 'error']
    assert len(errors) == 1
    assert 'expired' in errors[0].message.lower()


def test_warns_when_no_tags():
    with patch('envault.lint.list_secrets', return_value=['MY_SECRET']), \
         patch('envault.lint.get_expiry', return_value=None), \
         patch('envault.lint.is_expired', return_value=False), \
         patch('envault.lint.get_tags', return_value=[]):
        issues = lint_vault(VAULT, PASS)
    assert any('no tags' in i.message.lower() for i in issues)


def test_lint_error_on_bad_vault():
    with patch('envault.lint.list_secrets', side_effect=Exception('bad')):
        with pytest.raises(LintError):
            lint_vault(VAULT, PASS)
