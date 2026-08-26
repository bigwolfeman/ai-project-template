#!/usr/bin/env python3
"""Protected evaluator: run subject and emit evaluator-result JSON on stdout."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "subject" / "work.py"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_subject():
    spec = importlib.util.spec_from_file_location("tiny_subject_work", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load subject module: {SUBJECT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    started = time.monotonic()
    started_at = _utc_now()
    campaign_id = os.environ.get("CAMPAIGN_ID", "tiny-generic")
    trial_id = os.environ.get("TRIAL_ID", "trial-unknown")
    candidate_id = os.environ.get("CANDIDATE_ID", "candidate-unknown")

    try:
        subject = _load_subject()
        tests_passed = bool(subject.ok())
        latency_ms = float(subject.LATENCY_MS)
    except (OSError, AttributeError, TypeError, ValueError, ImportError, RuntimeError) as exc:
        wall = time.monotonic() - started
        empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        doc = {
            "schema_version": "1.0.0",
            "campaign_id": campaign_id,
            "trial_id": trial_id,
            "candidate_id": candidate_id,
            "evaluator_digest": _digest(Path(__file__)),
            "protocol_digest": _digest(ROOT / "campaign.yaml"),
            "environment_digest": _digest(SUBJECT) if SUBJECT.is_file() else empty,
            "started_at": started_at,
            "ended_at": _utc_now(),
            "measurements": {"tests_passed": False, "latency_ms": 0},
            "hard_constraint_results": [
                {"name": "tests_pass", "passed": False, "detail": str(exc)}
            ],
            "runtime_resource_use": {"wall_clock_seconds": wall},
            "artifact_references": [],
            "evaluator_status": "error",
            "diagnostic_messages": [f"subject load/run failed: {exc}"],
        }
        print(json.dumps(doc, sort_keys=True))
        return 1

    wall = time.monotonic() - started
    doc = {
        "schema_version": "1.0.0",
        "campaign_id": campaign_id,
        "trial_id": trial_id,
        "candidate_id": candidate_id,
        "evaluator_digest": _digest(Path(__file__)),
        "protocol_digest": _digest(ROOT / "campaign.yaml"),
        "environment_digest": _digest(SUBJECT),
        "started_at": started_at,
        "ended_at": _utc_now(),
        "measurements": {
            "tests_passed": tests_passed,
            "latency_ms": latency_ms,
        },
        "hard_constraint_results": [
            {
                "name": "tests_pass",
                "passed": tests_passed,
                "detail": "subject.ok()",
            }
        ],
        "runtime_resource_use": {"wall_clock_seconds": wall},
        "artifact_references": [],
        "evaluator_status": "success" if tests_passed else "error",
        "diagnostic_messages": [],
    }
    out_path = os.environ.get("CAMPAIGN_EVALUATOR_RESULT_FILE")
    text = json.dumps(doc, sort_keys=True)
    if out_path:
        Path(out_path).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
