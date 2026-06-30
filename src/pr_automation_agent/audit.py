"""EU AI Act Art. 52/53 audit trail for AI-generated contributions."""

import json
import datetime
import pathlib


_LOG_PATH = pathlib.Path(__file__).parent.parent.parent / "compliance" / "audit_log" / "contributions.jsonl"


def log_ai_contribution(
    *,
    file_path: str,
    ai_model: str,
    human_reviewer: str | None = None,
    pr_number: str | None = None,
    notes: str = "",
) -> None:
    """Append one JSON-line record to the audit log.

    Call this after an AI-generated file is merged, not during generation.
    The log is gitignored so it accumulates locally; copy to a durable
    store (S3, BigQuery) for long-term compliance evidence.
    """
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "file": file_path,
        "ai_model": ai_model,
        "human_reviewer": human_reviewer,
        "pr_number": pr_number,
        "notes": notes,
        "eu_ai_act_articles": ["Art. 50", "Art. 52"],
    }
    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
