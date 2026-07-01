"""EU AI Act Art. 52/53 audit trail for AI-generated contributions."""

import json
import datetime
import pathlib


def log_ai_contribution(
    *,
    file_path: str,
    ai_model: str,
    human_reviewer: str | None = None,
    pr_number: str | None = None,
    notes: str = "",
    output_dir: pathlib.Path | None = None,
) -> None:
    """Append one JSON-line record to the audit log.

    Writes to <output_dir>/contributions.jsonl, defaulting to
    compliance/audit_log/ relative to the current working directory.
    Call this after an AI-generated file is merged, not during generation.
    """
    log_path = (output_dir or pathlib.Path.cwd() / "compliance" / "audit_log") / "contributions.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "file": file_path,
        "ai_model": ai_model,
        "human_reviewer": human_reviewer,
        "pr_number": pr_number,
        "notes": notes,
        "eu_ai_act_articles": ["Art. 50", "Art. 52"],
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
