"""Tests for the Dagster integration layer."""

import json
import pathlib
import pytest
from unittest.mock import MagicMock, patch

from pr_automation_agent.integrations.dagster import (
    BaseRestAsset,
    BaseGraphQLAsset,
    BaseDbReplicationAsset,
    dev_env_secret_resolver_resource,
)


# ---------------------------------------------------------------------------
# BaseRestAsset
# ---------------------------------------------------------------------------

class _StubRestAsset(BaseRestAsset):
    provider = "stub"
    entity = "items"

    def fetch_all(self) -> list[dict]:
        return [{"id": 1}, {"id": 2}, {"id": 3}]


def test_dagster_rest_materialize_adds_metadata(tmp_path):
    asset = _StubRestAsset()
    asset.output_root = tmp_path

    ctx = MagicMock()
    result = asset.materialize(ctx)

    assert pathlib.Path(result).exists()
    ctx.add_output_metadata.assert_called_once()
    meta = ctx.add_output_metadata.call_args[0][0]
    assert "rows" in meta
    assert "path" in meta


def test_dagster_rest_materialize_returns_path(tmp_path):
    asset = _StubRestAsset()
    asset.output_root = tmp_path
    ctx = MagicMock()
    result = asset.materialize(ctx)
    assert result.endswith(".json")


# ---------------------------------------------------------------------------
# BaseGraphQLAsset
# ---------------------------------------------------------------------------

class _StubGraphQLAsset(BaseGraphQLAsset):
    provider = "stub"
    entity = "nodes"
    url = "https://stub.example.com/graphql"
    query = "{ nodes { id } }"

    def extract_records(self, data: dict) -> list[dict]:
        return data.get("nodes", [])


def test_dagster_graphql_materialize(tmp_path):
    asset = _StubGraphQLAsset()
    asset.output_root = tmp_path

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": {"nodes": [{"id": "x"}]}}
    mock_resp.raise_for_status = MagicMock()

    ctx = MagicMock()
    with patch("requests.post", return_value=mock_resp):
        result = asset.materialize(ctx)

    assert pathlib.Path(result).exists()
    ctx.add_output_metadata.assert_called_once()


# ---------------------------------------------------------------------------
# BaseDbReplicationAsset — resolver injected from context
# ---------------------------------------------------------------------------

class _StubDbAsset(BaseDbReplicationAsset):
    engine_name = "postgres"
    table = "orders"

    def get_query(self, since: str) -> str:
        return "SELECT * FROM orders WHERE updated_at >= :since"


def test_dagster_db_uses_context_resolver(tmp_path):
    from pr_automation_agent import SecretReference

    asset = _StubDbAsset()
    asset.output_root = tmp_path

    mock_resolver = MagicMock()
    mock_resolver.resolve_as_str.side_effect = lambda ref: (
        f"sqlite:///{tmp_path}/demo.db" if ref.key == "URI" else "1970-01-01"
    )

    # seed a minimal SQLite table
    import sqlite3, os
    db_path = tmp_path / "demo.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE orders (id INTEGER, updated_at TEXT)")
    conn.execute("INSERT INTO orders VALUES (1, '2024-01-01')")
    conn.commit()
    conn.close()

    ctx = MagicMock()
    ctx.resources.secret_resolver = mock_resolver

    result = asset.materialize(ctx)
    assert result.endswith(".parquet")
    ctx.add_output_metadata.assert_called_once()


# ---------------------------------------------------------------------------
# dev_env_secret_resolver_resource
# ---------------------------------------------------------------------------

def test_dev_env_resource_is_callable():
    from pr_automation_agent import DevEnvSecretResolver
    resolver = dev_env_secret_resolver_resource()  # no context arg — resource fn takes none
    assert isinstance(resolver, DevEnvSecretResolver)
