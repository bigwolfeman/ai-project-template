"""Prompt evaluation adapter. Scores a prompt file against fixed cases."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..errors import AdapterError
from ..process import ProcessResult
from .base import AdapterContext

_EMPTY_DIGEST = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class PromptEvalAdapter:
    """Score subject/prompt.txt against eval/cases.json; emit evaluator-result."""

    name = "prompt_eval"

    def prepare(self, ctx: AdapterContext) -> None:
        if ctx.log_dir is not None:
            ctx.log_dir.mkdir(parents=True, exist_ok=True)
        prompt = _prompt_path(ctx)
        cases = _cases_path(ctx)
        if not prompt.is_file():
            raise AdapterError(
                f"prompt file missing: {prompt}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                path=str(prompt),
            )
        if not cases.is_file():
            raise AdapterError(
                f"cases file missing: {cases}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                path=str(cases),
            )
        ctx.extras["prompt_path"] = str(prompt)
        ctx.extras["cases_path"] = str(cases)

    def validate_candidate(self, ctx: AdapterContext) -> None:
        if not ctx.candidate_id:
            raise AdapterError(
                "candidate_id is required",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                field="candidate_id",
            )
        if not ctx.work_dir.is_dir():
            raise AdapterError(
                f"work_dir does not exist: {ctx.work_dir}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                path=str(ctx.work_dir),
            )

    def execute(self, ctx: AdapterContext) -> ProcessResult:
        started = time.monotonic()
        prompt_text = Path(ctx.extras["prompt_path"]).read_text(encoding="utf-8")
        cases = _load_cases(Path(ctx.extras["cases_path"]), ctx)
        results = [_score_case(prompt_text, case, idx) for idx, case in enumerate(cases)]
        passed = all(item["passed"] for item in results)
        score = sum(1 for item in results if item["passed"])
        wall = time.monotonic() - started
        # Deterministic synthetic latency: length-based, not wall clock.
        latency_ms = float(max(1, len(prompt_text)))
        payload = {
            "tests_passed": passed,
            "cases_passed": score,
            "cases_total": len(results),
            "latency_ms": latency_ms,
            "case_results": results,
            "wall_clock_seconds": wall,
        }
        stdout = json.dumps(payload, sort_keys=True)
        return ProcessResult(
            argv=["prompt_eval", "score"],
            returncode=0 if passed else 1,
            stdout=stdout,
            stderr="",
            wall_clock_seconds=wall,
            timed_out=False,
        )

    def collect(self, ctx: AdapterContext, proc: ProcessResult) -> Any:
        text = (proc.stdout or "").strip()
        if not text:
            raise AdapterError(
                "prompt_eval produced empty stdout",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            )
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AdapterError(
                f"prompt_eval stdout is not JSON: {exc.msg}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            ) from exc

    def normalize_result(self, raw: Any, ctx: AdapterContext) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise AdapterError(
                f"unsupported raw result type {type(raw).__name__}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            )
        passed = bool(raw.get("tests_passed"))
        wall = float(raw.get("wall_clock_seconds", 0.0))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        detail_parts = [
            f"{item.get('id', idx)}:{'pass' if item.get('passed') else 'fail'}"
            for idx, item in enumerate(raw.get("case_results") or [])
            if isinstance(item, dict)
        ]
        return {
            "schema_version": "1.0.0",
            "campaign_id": ctx.campaign_id,
            "trial_id": ctx.trial_id,
            "candidate_id": ctx.candidate_id,
            "evaluator_digest": _EMPTY_DIGEST,
            "protocol_digest": _EMPTY_DIGEST,
            "environment_digest": _EMPTY_DIGEST,
            "started_at": now,
            "ended_at": now,
            "measurements": {
                "tests_passed": passed,
                "latency_ms": float(raw.get("latency_ms", wall * 1000.0)),
                "cases_passed": int(raw.get("cases_passed", 0)),
            },
            "hard_constraint_results": [
                {
                    "name": "tests_pass",
                    "passed": passed,
                    "detail": "; ".join(detail_parts) if detail_parts else "no cases",
                }
            ],
            "runtime_resource_use": {"wall_clock_seconds": wall},
            "artifact_references": [],
            "evaluator_status": "success" if passed else "error",
            "diagnostic_messages": [] if passed else ["one or more prompt cases failed"],
        }

    def cleanup(self, ctx: AdapterContext) -> None:
        return None


def _prompt_path(ctx: AdapterContext) -> Path:
    override = ctx.extras.get("prompt_path")
    if isinstance(override, (str, Path)):
        path = Path(override)
        return path if path.is_absolute() else ctx.work_dir / path
    return ctx.work_dir / "subject" / "prompt.txt"


def _cases_path(ctx: AdapterContext) -> Path:
    override = ctx.extras.get("cases_path")
    if isinstance(override, (str, Path)):
        path = Path(override)
        return path if path.is_absolute() else ctx.work_dir / path
    return ctx.work_dir / "eval" / "cases.json"


def _load_cases(path: Path, ctx: AdapterContext) -> list[dict[str, Any]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdapterError(
            f"invalid cases JSON: {exc.msg}",
            campaign_id=ctx.campaign_id,
            trial_id=ctx.trial_id,
            path=str(path),
        ) from exc
    if isinstance(doc, dict) and isinstance(doc.get("cases"), list):
        cases = doc["cases"]
    elif isinstance(doc, list):
        cases = doc
    else:
        raise AdapterError(
            "cases file must be a list or {\"cases\": [...]}",
            campaign_id=ctx.campaign_id,
            trial_id=ctx.trial_id,
            path=str(path),
        )
    if not cases:
        raise AdapterError(
            "cases list is empty",
            campaign_id=ctx.campaign_id,
            trial_id=ctx.trial_id,
            path=str(path),
        )
    return cases


def _score_case(prompt: str, case: dict[str, Any], idx: int) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise AdapterError(f"cases[{idx}] must be an object", field=f"cases[{idx}]")
    case_id = str(case.get("id") or f"case-{idx}")
    must_contain = case.get("must_contain") or []
    must_not_contain = case.get("must_not_contain") or []
    if not isinstance(must_contain, list) or not isinstance(must_not_contain, list):
        raise AdapterError(
            f"cases[{idx}] must_contain/must_not_contain must be lists",
            field=f"cases[{idx}]",
        )
    failures: list[str] = []
    lowered = prompt if case.get("case_sensitive") else prompt.lower()
    for needle in must_contain:
        text = str(needle)
        hay = lowered if not case.get("case_sensitive") else prompt
        check = text if case.get("case_sensitive") else text.lower()
        if check not in hay:
            failures.append(f"missing {text!r}")
    for needle in must_not_contain:
        text = str(needle)
        hay = lowered if not case.get("case_sensitive") else prompt
        check = text if case.get("case_sensitive") else text.lower()
        if check in hay:
            failures.append(f"forbidden {text!r}")
    return {
        "id": case_id,
        "passed": not failures,
        "detail": "; ".join(failures),
    }
