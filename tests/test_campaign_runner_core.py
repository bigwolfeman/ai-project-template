"""Unit tests for campaign runner core. Stdlib unittest only."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from campaign_runner.budget import (  # noqa: E402
    BudgetState,
    budget_from_ledger_events,
    check_budget,
)
from campaign_runner.comparator import compare  # noqa: E402
from campaign_runner.env import scrub_environ  # noqa: E402
from campaign_runner.errors import BudgetExhaustedError, LockMismatchError  # noqa: E402
from campaign_runner.ledger_write import (  # noqa: E402
    append_event,
    prior_digest_for_append,
    read_ledger_raw_lines,
)
from campaign_runner.lock import file_digest, verify_lock  # noqa: E402


class EnvScrubTests(unittest.TestCase):
    def test_removes_appimage_and_appdir(self) -> None:
        base = {
            "PATH": "/usr/bin",
            "APPIMAGE": "/tmp/Cursor.AppImage",
            "APPDIR": "/tmp/.mount_Cursor",
            "LD_LIBRARY_PATH": "/tmp/.mount_Cursor/usr/lib",
            "HOME": "/home/test",
        }
        cleaned = scrub_environ(base)
        self.assertNotIn("APPIMAGE", cleaned)
        self.assertNotIn("APPDIR", cleaned)
        self.assertNotIn("LD_LIBRARY_PATH", cleaned)
        self.assertEqual(cleaned["PATH"], "/usr/bin")
        self.assertEqual(cleaned["HOME"], "/home/test")

    def test_clears_appimage_looking_ld_without_markers(self) -> None:
        base = {
            "PATH": "/usr/bin",
            "LD_LIBRARY_PATH": "/tmp/squashfs-root/usr/lib:/opt/lib",
        }
        cleaned = scrub_environ(base)
        self.assertNotIn("LD_LIBRARY_PATH", cleaned)

    def test_preserves_normal_ld_library_path(self) -> None:
        base = {
            "PATH": "/usr/bin",
            "LD_LIBRARY_PATH": "/opt/cuda/lib64",
        }
        cleaned = scrub_environ(base)
        self.assertEqual(cleaned["LD_LIBRARY_PATH"], "/opt/cuda/lib64")


class ComparatorHardConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = {
            "hard_constraints": [
                {
                    "name": "tests_pass",
                    "measurement": "tests_passed",
                    "op": "eq",
                    "value": True,
                }
            ],
            "comparator_policy": {
                "strategy": "hard_constraints_then_objectives",
                "objectives": [{"measurement": "latency_ms", "direction": "minimize"}],
                "equivalence_margin": {"latency_ms": 1.0},
            },
            "replication_policy": {
                "min_repeats": 1,
                "single_noisy_run_advances_baseline": False,
            },
        }
        self.baseline = {
            "sealed": True,
            "measurements": [
                {"name": "tests_passed", "value": True},
                {"name": "latency_ms", "value": 100.0},
            ],
        }

    def test_failed_hard_constraint_rejects_even_if_faster(self) -> None:
        result = {
            "evaluator_status": "success",
            "measurements": {"tests_passed": False, "latency_ms": 10.0},
            "hard_constraint_results": [{"name": "tests_pass", "passed": False}],
        }
        out = compare(result=result, baseline=self.baseline, manifest=self.manifest)
        self.assertEqual(out.comparator_outcome, "regresses")
        self.assertEqual(out.trial_outcome, "rejected")
        self.assertFalse(out.advance_best)

    def test_dominates_when_constraints_pass_and_objective_improves(self) -> None:
        result = {
            "evaluator_status": "success",
            "measurements": {"tests_passed": True, "latency_ms": 50.0},
            "hard_constraint_results": [{"name": "tests_pass", "passed": True}],
        }
        out = compare(result=result, baseline=self.baseline, manifest=self.manifest)
        self.assertEqual(out.comparator_outcome, "dominates")
        self.assertEqual(out.trial_outcome, "accepted")
        self.assertTrue(out.advance_best)


class BudgetStopTests(unittest.TestCase):
    def test_max_trial_count_stops(self) -> None:
        manifest = {
            "resource_budget": {
                "max_trial_count": 2,
                "max_consecutive_crashes": 5,
            },
            "stop_conditions": [{"type": "budget_exhausted"}],
        }
        usage = BudgetState(trial_count=2)
        with self.assertRaises(BudgetExhaustedError) as ctx:
            check_budget(manifest, usage, campaign_id="c1")
        self.assertIn("max_trial_count", str(ctx.exception))

    def test_stagnation_stop_condition(self) -> None:
        manifest = {
            "resource_budget": {
                "max_trial_count": 100,
                "max_stagnation_trials": 50,
            },
            "stop_conditions": [{"type": "stagnation", "threshold": 3}],
        }
        usage = BudgetState(stagnation_trials=3)
        with self.assertRaises(BudgetExhaustedError):
            check_budget(manifest, usage, campaign_id="c1")

    def test_budget_from_ledger_counts_trials(self) -> None:
        events = [
            {"event_type": "trial_completed", "payload": {"trial_outcome": "rejected"}},
            {"event_type": "candidate_rejected", "payload": {}},
            {"event_type": "trial_completed", "payload": {"trial_outcome": "rejected"}},
            {"event_type": "candidate_rejected", "payload": {}},
        ]
        usage = budget_from_ledger_events(events)
        self.assertEqual(usage.trial_count, 2)
        self.assertGreaterEqual(usage.stagnation_trials, 2)


class LedgerHashChainTests(unittest.TestCase):
    def test_append_sets_prior_digest_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign_dir = Path(tmp)
            (campaign_dir / "state").mkdir(parents=True)
            first = append_event(
                campaign_dir,
                event_type="campaign_created",
                campaign_id="chain-test",
                actor="runner",
                payload={"title": "t"},
                validate=False,
            )
            self.assertIsNone(first["prior_event_digest"])
            lines = read_ledger_raw_lines(campaign_dir)
            self.assertEqual(len(lines), 1)
            expected = hashlib.sha256(lines[0].encode("utf-8")).hexdigest()
            self.assertEqual(prior_digest_for_append(campaign_dir), expected)
            second = append_event(
                campaign_dir,
                event_type="campaign_validated",
                campaign_id="chain-test",
                actor="runner",
                payload={},
                validate=False,
            )
            self.assertEqual(second["prior_event_digest"], expected)


class LockMismatchTests(unittest.TestCase):
    def test_digest_mismatch_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign_dir = Path(tmp)
            target = campaign_dir / "eval" / "run.py"
            target.parent.mkdir(parents=True)
            target.write_text("print('ok')\n", encoding="utf-8")
            actual = file_digest(target)
            wrong = "0" * 64
            self.assertNotEqual(actual, wrong)
            lock = {
                "schema_version": "1.0.0",
                "campaign_id": "lock-test",
                "locked_at": "2026-08-24T00:00:00Z",
                "resources": [
                    {
                        "path": "eval/run.py",
                        "digest_algorithm": "sha256",
                        "digest": wrong,
                    }
                ],
            }
            with self.assertRaises(LockMismatchError) as ctx:
                verify_lock(campaign_dir, lock, campaign_id="lock-test", when="before")
            self.assertIn("digest mismatch", str(ctx.exception))

    def test_matching_digest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign_dir = Path(tmp)
            target = campaign_dir / "protected.txt"
            target.write_text("sealed\n", encoding="utf-8")
            digest = file_digest(target)
            lock = {
                "campaign_id": "lock-test",
                "resources": [
                    {
                        "path": "protected.txt",
                        "digest_algorithm": "sha256",
                        "digest": digest,
                    }
                ],
            }
            verify_lock(campaign_dir, lock, campaign_id="lock-test", when="after")


class NoHardResetTests(unittest.TestCase):
    def test_runner_package_has_no_reset_hard_invocation(self) -> None:
        package = SCRIPTS / "campaign_runner"
        cli = SCRIPTS / "run_campaign.py"
        needle = "reset" + " --hard"
        hits: list[str] = []
        for path in list(package.rglob("*.py")) + [cli]:
            text = path.read_text(encoding="utf-8")
            if needle in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [], msg="found forbidden hard-reset string in: " + ", ".join(hits))


class OverlayPathsTests(unittest.TestCase):
    def test_overlays_mutable_and_protected_into_worktree(self) -> None:
        from campaign_runner.isolation import overlay_paths

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = root / "campaign"
            work = root / "worktree"
            (campaign / "subject").mkdir(parents=True)
            (campaign / "eval").mkdir(parents=True)
            work.mkdir()
            (campaign / "subject" / "work.py").write_text("LATENCY_MS = 1\n", encoding="utf-8")
            (campaign / "eval" / "run.py").write_text("print(1)\n", encoding="utf-8")
            (work / "subject").mkdir()
            (work / "subject" / "work.py").write_text("LATENCY_MS = 99\n", encoding="utf-8")
            overlay_paths(
                campaign,
                work,
                ["subject/", "eval/"],
                campaign_id="overlay-test",
            )
            self.assertEqual(
                (work / "subject" / "work.py").read_text(encoding="utf-8"),
                "LATENCY_MS = 1\n",
            )
            self.assertTrue((work / "eval" / "run.py").is_file())

    def test_rejects_path_escape(self) -> None:
        from campaign_runner.errors import WorktreeError
        from campaign_runner.isolation import overlay_paths

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = root / "campaign"
            work = root / "worktree"
            campaign.mkdir()
            work.mkdir()
            with self.assertRaises(WorktreeError):
                overlay_paths(campaign, work, ["../outside"], campaign_id="overlay-test")


if __name__ == "__main__":
    unittest.main()
