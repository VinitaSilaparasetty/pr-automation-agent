import json
import pathlib
import pytest
from pr_automation_agent import log_ai_contribution


def test_writes_jsonl_record(tmp_path):
    log_ai_contribution(
        file_path="ingest/rest/stripe/invoices_asset.py",
        ai_model="GitHub Copilot",
        human_reviewer="@alice",
        pr_number="42",
        notes="initial REST asset",
        output_dir=tmp_path,
    )

    log_path = tmp_path / "contributions.jsonl"
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["file"] == "ingest/rest/stripe/invoices_asset.py"
    assert record["ai_model"] == "GitHub Copilot"
    assert record["human_reviewer"] == "@alice"
    assert record["pr_number"] == "42"
    assert "Art. 50" in record["eu_ai_act_articles"]
    assert "Art. 52" in record["eu_ai_act_articles"]
    assert record["timestamp"].endswith("Z")


def test_appends_multiple_records(tmp_path):
    for i in range(3):
        log_ai_contribution(file_path=f"file_{i}.py", ai_model="Copilot", output_dir=tmp_path)

    lines = (tmp_path / "contributions.jsonl").read_text().strip().splitlines()
    assert len(lines) == 3


def test_optional_fields_default_to_none(tmp_path):
    log_ai_contribution(file_path="some_asset.py", ai_model="Copilot", output_dir=tmp_path)
    record = json.loads((tmp_path / "contributions.jsonl").read_text())
    assert record["human_reviewer"] is None
    assert record["pr_number"] is None
