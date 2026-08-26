"""Generic command adapter: run evaluator_command and parse JSON result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import AdapterError
from ..process import ProcessResult, run_command
from .base import AdapterContext


class GenericCommandAdapter:
    """Runs campaign.yaml evaluator_command; parses evaluator-result JSON."""

    name = "generic_command"

    def prepare(self, ctx: AdapterContext) -> None:
        if ctx.log_dir is not None:
            ctx.log_dir.mkdir(parents=True, exist_ok=True)
        cmd = ctx.manifest.get("evaluator_command")
        if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) for x in cmd):
            raise AdapterError(
                "evaluator_command must be a non-empty argv list of strings",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
                field="evaluator_command",
            )

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
        argv = list(ctx.manifest["evaluator_command"])
        env = dict(ctx.env)
        env.setdefault("CAMPAIGN_ID", ctx.campaign_id)
        env.setdefault("TRIAL_ID", ctx.trial_id)
        env.setdefault("CANDIDATE_ID", ctx.candidate_id)
        if ctx.result_file is not None:
            env["CAMPAIGN_EVALUATOR_RESULT_FILE"] = str(ctx.result_file)
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
        if ctx.result_file is not None and ctx.result_file.is_file():
            return ctx.result_file.read_text(encoding="utf-8")
        declared = ctx.extras.get("result_file")
        if isinstance(declared, (str, Path)):
            path = Path(declared)
            if not path.is_absolute():
                path = ctx.work_dir / path
            if path.is_file():
                return path.read_text(encoding="utf-8")
        env_path = ctx.env.get("CAMPAIGN_EVALUATOR_RESULT_FILE")
        if env_path:
            path = Path(env_path)
            if path.is_file():
                return path.read_text(encoding="utf-8")
        text = (proc.stdout or "").strip()
        if text:
            return text
        raise AdapterError(
            "evaluator produced no stdout and no result file",
            campaign_id=ctx.campaign_id,
            trial_id=ctx.trial_id,
        )

    def normalize_result(self, raw: Any, ctx: AdapterContext) -> dict[str, Any]:
        if isinstance(raw, dict):
            doc = raw
        elif isinstance(raw, (str, bytes)):
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            text = text.strip()
            # Prefer last JSON object if logs precede it.
            doc = _parse_json_document(text)
        else:
            raise AdapterError(
                f"unsupported raw result type {type(raw).__name__}",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            )
        if not isinstance(doc, dict):
            raise AdapterError(
                "evaluator result must be a JSON object",
                campaign_id=ctx.campaign_id,
                trial_id=ctx.trial_id,
            )
        # Fill identity fields when the evaluator omits them.
        doc.setdefault("campaign_id", ctx.campaign_id)
        doc.setdefault("trial_id", ctx.trial_id)
        doc.setdefault("candidate_id", ctx.candidate_id)
        return doc

    def cleanup(self, ctx: AdapterContext) -> None:
        return None


def _parse_json_document(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try last non-empty line.
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    # Try first '{' to last '}'.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise AdapterError(f"could not parse evaluator JSON: {exc.msg}") from exc
    raise AdapterError("could not parse evaluator JSON from stdout")
