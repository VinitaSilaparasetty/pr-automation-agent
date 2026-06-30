"""Smoke tests for the framework-agnostic base classes."""

import json
import pathlib
import pytest
from unittest.mock import MagicMock, patch

from pr_automation_agent import (
    BaseRestFetcher,
    BaseGraphQLFetcher,
    BaseDbReplicator,
)


# ---------------------------------------------------------------------------
# BaseRestFetcher
# ---------------------------------------------------------------------------

class _StubRestFetcher(BaseRestFetcher):
    provider = "stub"
    entity = "items"

    def fetch_all(self) -> list[dict]:
        return [{"id": 1}, {"id": 2}]


def test_rest_run_returns_path_and_count(tmp_path):
    fetcher = _StubRestFetcher()
    fetcher.output_root = tmp_path

    path, rows = fetcher.run()

    assert rows == 2
    out = pathlib.Path(path)
    assert out.exists()
    assert json.loads(out.read_text()) == [{"id": 1}, {"id": 2}]


def test_rest_run_writes_date_stamped_json(tmp_path):
    import datetime as dt
    fetcher = _StubRestFetcher()
    fetcher.output_root = tmp_path

    path, _ = fetcher.run()
    assert dt.date.today().isoformat() in path
    assert path.endswith(".json")


# ---------------------------------------------------------------------------
# BaseGraphQLFetcher
# ---------------------------------------------------------------------------

class _StubGraphQLFetcher(BaseGraphQLFetcher):
    provider = "stub"
    entity = "nodes"
    url = "https://stub.example.com/graphql"
    query = "{ nodes { id } }"

    def extract_records(self, data: dict) -> list[dict]:
        return data.get("nodes", [])


def test_graphql_run_returns_path_and_count(tmp_path):
    fetcher = _StubGraphQLFetcher()
    fetcher.output_root = tmp_path

    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"nodes": [{"id": "a"}, {"id": "b"}]}}
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response):
        path, rows = fetcher.run()

    assert rows == 2
    assert pathlib.Path(path).exists()


# ---------------------------------------------------------------------------
# BaseDbReplicator
# ---------------------------------------------------------------------------

class _StubDbReplicator(BaseDbReplicator):
    engine_name = "postgres"
    table = "orders"

    def get_query(self, since: str) -> str:
        return "SELECT * FROM orders WHERE updated_at >= :since"


def test_db_replicator_abstract_method_required():
    with pytest.raises(TypeError):
        BaseDbReplicator()  # type: ignore[abstract]


def test_db_replicator_accepts_custom_resolver():
    from pr_automation_agent import DevEnvSecretResolver
    resolver = DevEnvSecretResolver()
    r = _StubDbReplicator(secret_resolver=resolver)
    assert r._resolver is resolver


def test_db_replicator_defaults_to_dev_env_resolver():
    from pr_automation_agent import DevEnvSecretResolver
    r = _StubDbReplicator()
    assert isinstance(r._resolver, DevEnvSecretResolver)
