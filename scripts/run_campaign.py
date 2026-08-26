#!/usr/bin/env python3
"""CLI for local campaign runs: validate, baseline, trial, status."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from campaign_runner.errors import CampaignRunnerError, UsageError  # noqa: E402
from campaign_runner.runner import (  # noqa: E402
    run_baseline,
    run_trial,
    status_summary,
    validate_campaign,
)

USAGE = """usage: run_campaign.py <command> <campaign-dir> [options]

commands:
  validate <campaign-dir>
  baseline <campaign-dir>
  trial <campaign-dir> --candidate-id <id>
  status <campaign-dir>
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print(USAGE, file=sys.stderr)
        return 2
    command = args[0]
    try:
        if command == "validate":
            return _cmd_validate(args[1:])
        if command == "baseline":
            return _cmd_baseline(args[1:])
        if command == "trial":
            return _cmd_trial(args[1:])
        if command == "status":
            return _cmd_status(args[1:])
        raise UsageError(f"unknown command {command!r}")
    except UsageError as exc:
        print(f"run_campaign.py: {exc}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    except CampaignRunnerError as exc:
        print(f"run_campaign.py: {exc}", file=sys.stderr)
        return 1


def _require_dir(args: list[str], command: str) -> Path:
    if len(args) < 1:
        raise UsageError(f"{command} requires <campaign-dir>")
    path = Path(args[0])
    if not path.is_dir():
        raise UsageError(f"missing campaign directory: {path}")
    return path


def _cmd_validate(args: list[str]) -> int:
    campaign_dir = _require_dir(args, "validate")
    if len(args) != 1:
        raise UsageError("validate takes exactly one argument: <campaign-dir>")
    validate_campaign(campaign_dir)
    print("ok")
    return 0


def _cmd_baseline(args: list[str]) -> int:
    campaign_dir = _require_dir(args, "baseline")
    if len(args) != 1:
        raise UsageError("baseline takes exactly one argument: <campaign-dir>")
    result = run_baseline(campaign_dir)
    status = result.get("evaluator_status", "unknown")
    print(f"baseline ok evaluator_status={status}")
    return 0


def _cmd_trial(args: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="run_campaign.py trial", add_help=False)
    parser.add_argument("campaign_dir")
    parser.add_argument("--candidate-id", required=True)
    try:
        ns = parser.parse_args(args)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        print(USAGE, file=sys.stderr)
        return code if code else 2
    campaign_dir = Path(ns.campaign_dir)
    if not campaign_dir.is_dir():
        raise UsageError(f"missing campaign directory: {campaign_dir}")
    out = run_trial(campaign_dir, candidate_id=ns.candidate_id)
    comparison = out["comparison"]
    print(
        "trial ok "
        f"comparator={comparison['comparator_outcome']} "
        f"outcome={comparison['trial_outcome']} "
        f"best_advanced={comparison['advance_best']}"
    )
    return 0


def _cmd_status(args: list[str]) -> int:
    campaign_dir = _require_dir(args, "status")
    if len(args) != 1:
        raise UsageError("status takes exactly one argument: <campaign-dir>")
    print(status_summary(campaign_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
