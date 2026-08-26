"""Domain adapter protocol for campaign trials."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ..process import ProcessResult


@dataclass
class AdapterContext:
    campaign_dir: Path
    work_dir: Path
    manifest: dict[str, Any]
    campaign_id: str
    trial_id: str
    candidate_id: str
    log_dir: Path | None = None
    timeout_seconds: float | None = None
    result_file: Path | None = None
    env: dict[str, str] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Adapter(Protocol):
    name: str

    def prepare(self, ctx: AdapterContext) -> None:
        """Prepare work directory and environment for the trial."""

    def validate_candidate(self, ctx: AdapterContext) -> None:
        """Fail loud if the candidate is not eligible to run."""

    def execute(self, ctx: AdapterContext) -> ProcessResult:
        """Run the evaluator or domain command."""

    def collect(self, ctx: AdapterContext, proc: ProcessResult) -> Any:
        """Collect raw evaluator output (dict, path, or text)."""

    def normalize_result(self, raw: Any, ctx: AdapterContext) -> dict[str, Any]:
        """Normalize raw output to an evaluator-result document."""

    def cleanup(self, ctx: AdapterContext) -> None:
        """Release temporary resources for this trial."""
