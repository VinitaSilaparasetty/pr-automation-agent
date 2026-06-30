"""Smoke tests for the abstract base classes."""

import json
import pathlib
import pytest
from unittest.mock import MagicMock, patch

from pr_automation_agent import BaseRestAsset, BaseGraphQLAsset, BaseDbReplicationAsset


# ---------------------------------------------------------------------------
# BaseRestAsset
# ---------------------------------------------------------------------------

class _StubRestAsset(BaseRestAsset):
    provider = "stub"
    entity = "items"

    def fetch_all(self) -> list[dict]:
        return [{"id": 1}, {"id": 2}]


def test_rest_materialize_writes_json(tmp_path):
    asset = _StubRestAsset()
    asset.output_root = tmp_path

    ctx = MagicMock()
    result = asset.materialize(ctx)

    out_file = pathlib.Path(result)
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert len(data) == 2
    ctx.add_output_metadata.assert_called_once()
    meta = ctx.add_output_metadata.call_args[0][0]
    assert "rows" in meta
    assert "path" in meta


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


def test_graphql_materialize_writes_json(tmp_path):
    asset = _StubGraphQLAsset()
    asset.output_root = tmp_path

    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"nodes": [{"id": "a"}, {"id": "b"}]}}
    mock_response.raise_for_status = MagicMock()

    ctx = MagicMock()
    with patch("requests.post", return_value=mock_response):
        result = asset.materialize(ctx)

    out_file = pathlib.Path(result)
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert len(data) == 2


# ---------------------------------------------------------------------------
# BaseDbReplicationAsset — only checks error on missing deps
# ---------------------------------------------------------------------------

class _StubDbAsset(BaseDbReplicationAsset):
    engine_name = "postgres"
    table = "orders"

    def get_query(self, since: str) -> str:
        return "SELECT * FROM orders WHERE updated_at >= :since"


def test_db_asset_abstract_method_required():
    with pytest.raises(TypeError):
        BaseDbReplicationAsset()  # type: ignore[abstract]
