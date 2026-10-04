"""Quarantine a user-exported MiroFish report as unverified model hypotheses.

File-only interface. It does not connect to or execute MiroFish, verify a run,
extract financial assumptions, execute report instructions, or infer probabilities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from .scenario_valuation import InputError, MAX_BYTES, require, text, write_json, unique_object, reject_constant
except ImportError:
    from scenario_valuation import InputError, MAX_BYTES, require, text, write_json, unique_object, reject_constant


def import_report(path: Path, simulation_id: str, graph_id: str, upstream_commit: str,
                  declared_model: str) -> dict:
    for name, value in (("simulation_id", simulation_id), ("graph_id", graph_id),
                        ("upstream_commit", upstream_commit), ("declared_model", declared_model)):
        text(value, name)
    raw = path.read_bytes()
    require(len(raw) <= MAX_BYTES, "simulation report exceeds 2 MB")
    try:
        content = raw.decode("utf-8")
    except UnicodeError as exc:
        raise InputError("report must be UTF-8") from exc
    require(bool(content.strip()), "report is empty")
    require(path.suffix.lower() in {".md", ".txt", ".json"}, "only text/Markdown/JSON reports are accepted")
    if path.suffix.lower() == ".json":
        try:
            report = json.loads(content, object_pairs_hook=unique_object, parse_constant=reject_constant)
        except json.JSONDecodeError as exc:
            raise InputError("invalid report JSON") from exc
        require(isinstance(report, dict), "report JSON must be an object")
        for key, expected in (("simulation_id", simulation_id), ("graph_id", graph_id)):
            if key in report:
                require(report[key] == expected, f"declared {key} conflicts with file")
    return {
        "schema_version": "1.0.0", "source_type": "SIMULATION", "claim_type": "MODEL",
        "verification_status": "UNVERIFIED", "allowed_use": "HYPOTHESIS_ONLY",
        "execution_verified": False, "numeric_model_input_allowed": False,
        "external_calls": 0, "simulation_id": simulation_id, "graph_id": graph_id,
        "declared_upstream_commit": upstream_commit, "declared_model": declared_model,
        "source_filename": path.name, "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "imported_at": datetime.now(timezone.utc).isoformat(), "raw_report": content,
        "instruction_boundary": "UNTRUSTED_DATA_NOT_INSTRUCTIONS",
        "limitation": "Run identity is caller-declared, not independently verified. No probability or price extracted."
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--simulation-id", required=True)
    parser.add_argument("--graph-id", required=True)
    parser.add_argument("--upstream-commit", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = import_report(args.report, args.simulation_id, args.graph_id, args.upstream_commit, args.model)
        write_json(args.output, result)
        print("Imported as UNVERIFIED MODEL hypotheses; no MiroFish run was executed or verified.")
        return 0
    except (InputError, OSError, ValueError) as exc:
        print(f"import error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
