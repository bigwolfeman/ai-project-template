"""Pytest / micro-benchmark adapter. Emits evaluator-result JSON."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any

from ..errors import AdapterError
from ..process import ProcessResult, run_command
from .base import AdapterContext
from .generic_command import GenericCommandAdapter, _parse_json_document

_EMPTY_DIGEST = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class PytestBenchmarkAdapter:
    """Run pytest or subject/bench.py; normalize to evaluator-result JSON."""

    name = "pytest_benchmark"

    def prepare(self, ctx: AdapterContext) -> None:
        if ctx.log_dir is not None:
            ctx.log_dir.mkdir(parents=True, exist_ok=True)
        bench = ctx.work_dir / "subject" / "bench.py"
        pytest_ini = ctx.work_dir / "pytest.ini"
        tests_dir = ctx.work_dir / "tests"
        has_pytest_target = pytest_ini.is_file() or tests_dir.is_dir()
        if not bench.is_file() and not has_pytest_target:
            raise AdapterError(
                "pytest_benchmark needs subject/bench.py or a pytest suite under work_dir",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                path=str(ctx.work_dir),
            )
        ctx.extras["bench_mode"] = "bench.py" if bench.is_file() else "pytest"

    def validate_candidate(self, ctx: AdapterContext) -> None:
        GenericCommandAdapter().validate_candidate(ctx)

    def execute(self, ctx: AdapterContext) -> ProcessResult:
        mode = ctx.extras.get("bench_mode", "bench.py")
        env = dict(ctx.env)
        env.setdefault("CAMPAIGN_ID", ctx.campaign_id)
        env.setdefault("TRIAL_ID", ctx.trial_id)
        env.setdefault("CANDIDATE_ID", ctx.candidate_id)
        if mode == "bench.py":
            argv = [sys.executable, "subject/bench.py"]
        else:
            argv = [sys.executable, "-m", "pytest", "-q", "--tb=no"]
        return run_command(
            argv,
            cwd=ctx.work_dir,
            timeout_seconds=ctx.timeout_seconds,
            env=env,
            log_dir=ctx.log_dir,
            scrub=True,
            campaign_id=ctx.campaign_id,
            trial_id=ctx.trial_id,
        )

    def collect(self, ctx: AdapterContext, proc: ProcessResult) -> Any:
        text = (proc.stdout or "").strip()
        if text:
            try:
                return _parse_json_document(text)
            except AdapterError:
                pass
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "wall_clock_seconds": proc.wall_clock_seconds,
        }

    def normalize_result(self, raw: Any, ctx: AdapterContext) -> dict[str, Any]:
        if isinstance(raw, dict) and _looks_like_evaluator_result(raw):
            doc = dict(raw)
            doc.setdefault("campaign_id", ctx.campaign_id)
            doc.setdefault("trial_id", ctx.trial_id)
            doc.setdefault("candidate_id", ctx.candidate_id)
            return doc
        if not isinstance(raw, dict):
            raise AdapterError(
                f"unsupported raw result type {type(raw).__name__}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            )
        returncode = int(raw.get("returncode", 1))
        wall = float(raw.get("wall_clock_seconds", 0.0))
        passed = returncode == 0
        # Prefer an explicit latency_ms line from bench stdout when present.
        latency_ms = _extract_latency_ms(str(raw.get("stdout", "")), wall)
        now = _utc_now()
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
                "latency_ms": latency_ms,
            },
            "hard_constraint_results": [
                {
                    "name": "tests_pass",
                    "passed": passed,
                    "detail": f"returncode={returncode}",
                }
            ],
            "runtime_resource_use": {"wall_clock_seconds": wall},
            "artifact_references": [],
            "evaluator_status": "success" if passed else "error",
            "diagnostic_messages": _diagnostics(raw),
        }

    def cleanup(self, ctx: AdapterContext) -> None:
        return None


def _looks_like_evaluator_result(doc: dict[str, Any]) -> bool:
    return "measurements" in doc and "evaluator_status" in doc


def _extract_latency_ms(stdout: str, wall_seconds: float) -> float:
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("latency_ms="):
            try:
                return float(line.split("=", 1)[1].strip())
            except ValueError as exc:
                raise AdapterError(f"invalid latency_ms line: {line}") from exc
        if line.startswith("{") and "latency_ms" in line:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "latency_ms" in obj:
                return float(obj["latency_ms"])
    return round(wall_seconds * 1000.0, 3)


def _diagnostics(raw: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    stderr = str(raw.get("stderr") or "").strip()
    if stderr:
        messages.append(stderr[:2000])
    if int(raw.get("returncode", 0)) != 0:
        messages.append(f"command exited with {raw.get('returncode')}")
    return messages


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
