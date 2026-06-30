import os
import pytest
from pr_automation_agent import DevEnvSecretResolver, SecretReference


def test_resolves_from_env(monkeypatch):
    monkeypatch.setenv("PR_AGENT__MYDB__PASSWORD", "secret123")
    resolver = DevEnvSecretResolver()
    assert resolver.resolve_as_str(SecretReference("mydb", "password")) == "secret123"


def test_case_insensitive_keys(monkeypatch):
    monkeypatch.setenv("PR_AGENT__STRIPE__API_KEY", "sk_test_abc")
    resolver = DevEnvSecretResolver()
    assert resolver.resolve_as_str(SecretReference("stripe", "api_key")) == "sk_test_abc"
    assert resolver.resolve_as_str(SecretReference("STRIPE", "API_KEY")) == "sk_test_abc"


def test_raises_on_missing_env():
    resolver = DevEnvSecretResolver()
    ref = SecretReference("nonexistent", "key")
    with pytest.raises(RuntimeError, match="PR_AGENT__NONEXISTENT__KEY"):
        resolver.resolve_as_str(ref)


def test_error_message_includes_export_hint():
    resolver = DevEnvSecretResolver()
    with pytest.raises(RuntimeError, match="export PR_AGENT__"):
        resolver.resolve_as_str(SecretReference("foo", "bar"))


def test_secret_reference_is_named_tuple():
    ref = SecretReference("group", "key")
    assert ref.group_name == "group"
    assert ref.key == "key"
