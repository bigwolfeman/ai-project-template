"""Run commands with timeout, process-tree kill, and log capture."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .env import scrub_environ
from .errors import ProcessError, ProcessTimeoutError


@dataclass(frozen=True)
class ProcessResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    wall_clock_seconds: float
    timed_out: bool
    log_stdout: Path | None = None
    log_stderr: Path | None = None


def _kill_process_tree(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except PermissionError:
        proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: float | None,
    env: Mapping[str, str] | None = None,
    log_dir: Path | None = None,
    scrub: bool = True,
    campaign_id: str | None = None,
    trial_id: str | None = None,
) -> ProcessResult:
    """Run *argv* in *cwd*. Kill the process group on timeout."""
    if not argv:
        raise ProcessError(
            "empty command",
            campaign_id=campaign_id,
            trial_id=trial_id,
            field="argv",
        )
    run_env = scrub_environ(env) if scrub else dict(env or os.environ)
    stdout_path = stderr_path = None
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = log_dir / "stdout.log"
        stderr_path = log_dir / "stderr.log"

    started = time.monotonic()
    try:
        proc = subprocess.Popen(
            list(argv),
            cwd=cwd,
            env=run_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
    except OSError as exc:
        raise ProcessError(
            f"failed to start command {list(argv)!r}: {exc}",
            campaign_id=campaign_id,
            trial_id=trial_id,
        ) from exc

    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        _kill_process_tree(proc)
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(
            "utf-8", errors="replace"
        )
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(
            "utf-8", errors="replace"
        )
        wall = time.monotonic() - started
        if stdout_path is not None:
            stdout_path.write_text(stdout, encoding="utf-8")
        if stderr_path is not None:
            stderr_path.write_text(stderr, encoding="utf-8")
        raise ProcessTimeoutError(
            f"command timed out after {timeout_seconds}s: {list(argv)!r}",
            campaign_id=campaign_id,
            trial_id=trial_id,
        ) from exc

    wall = time.monotonic() - started
    if stdout_path is not None:
        stdout_path.write_text(stdout, encoding="utf-8")
    if stderr_path is not None:
        stderr_path.write_text(stderr, encoding="utf-8")

    result = ProcessResult(
        argv=list(argv),
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=stdout,
        stderr=stderr,
        wall_clock_seconds=wall,
        timed_out=timed_out,
        log_stdout=stdout_path,
        log_stderr=stderr_path,
    )
    return result
