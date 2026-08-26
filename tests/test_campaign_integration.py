"""End-to-end campaign runner integration tests using the tiny-generic fixture."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "campaigns" / "tiny-generic"
CLI = SCRIPTS / "run_campaign.py"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _scrubbed_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("APPIMAGE", None)
    env.pop("APPDIR", None)
    env.pop("LD_LIBRARY_PATH", None)
    return env


def _run_cli(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if not CLI.is_file():
        raise unittest.SkipTest("scripts/run_campaign.py not present (Leaf A blocker)")
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd or ROOT,
        env=_scrubbed_env(),
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_scrubbed_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )


def _prepare_campaign_copy() -> Path:
    """Copy fixture under ignored/ so validate_campaign can relative_to project ROOT."""
    if not FIXTURE.is_dir():
        raise unittest.SkipTest(f"missing fixture: {FIXTURE}")
    staging_root = ROOT / "ignored" / "test-campaigns"
    staging_root.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="tiny-generic-", dir=str(staging_root)))
    dest = tmp / "campaign"
    shutil.copytree(FIXTURE, dest)
    _git(dest, "init", "-b", "main")
    _git(dest, "config", "user.email", "fixture@example.com")
    _git(dest, "config", "user.name", "Fixture")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-m", "fixture initial")
    return dest


class AdapterRegistryTests(unittest.TestCase):
    def test_get_adapter_loads_all_three(self) -> None:
        from campaign_runner.adapters import get_adapter

        for name in ("generic_command", "pytest_benchmark", "prompt_eval"):
            adapter = get_adapter(name)
            self.assertEqual(adapter.name, name)
            for method in (
                "prepare",
                "validate_candidate",
                "execute",
                "collect",
                "normalize_result",
                "cleanup",
            ):
                self.assertTrue(callable(getattr(adapter, method)), msg=method)


class PromptEvalAdapterTests(unittest.TestCase):
    def test_scores_prompt_against_cases(self) -> None:
        from campaign_runner.adapters.base import AdapterContext
        from campaign_runner.adapters.prompt_eval import PromptEvalAdapter

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "subject").mkdir()
            (root / "eval").mkdir()
            (root / "subject" / "prompt.txt").write_text(
                "Always cite the budget and refuse secrets.\n",
                encoding="utf-8",
            )
            (root / "eval" / "cases.json").write_text(
                '{"cases":[{"id":"budget","must_contain":["budget"],'
                '"must_not_contain":["api_key"]}]}',
                encoding="utf-8",
            )
            ctx = AdapterContext(
                campaign_dir=root,
                work_dir=root,
                manifest={},
                campaign_id="tiny-generic",
                trial_id="trial-1",
                candidate_id="cand-1",
            )
            adapter = PromptEvalAdapter()
            adapter.prepare(ctx)
            adapter.validate_candidate(ctx)
            proc = adapter.execute(ctx)
            raw = adapter.collect(ctx, proc)
            doc = adapter.normalize_result(raw, ctx)
            self.assertEqual(doc["evaluator_status"], "success")
            self.assertTrue(doc["measurements"]["tests_passed"])
            self.assertIn("latency_ms", doc["measurements"])


class PytestBenchmarkAdapterTests(unittest.TestCase):
    def test_bench_script_normalizes_result(self) -> None:
        from campaign_runner.adapters.base import AdapterContext
        from campaign_runner.adapters.pytest_benchmark import PytestBenchmarkAdapter

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "subject").mkdir()
            (root / "subject" / "bench.py").write_text(
                "print('latency_ms=12.5')\n",
                encoding="utf-8",
            )
            ctx = AdapterContext(
                campaign_dir=root,
                work_dir=root,
                manifest={},
                campaign_id="tiny-generic",
                trial_id="trial-bench",
                candidate_id="cand-bench",
                timeout_seconds=30,
                env=_scrubbed_env(),
            )
            adapter = PytestBenchmarkAdapter()
            adapter.prepare(ctx)
            adapter.validate_candidate(ctx)
            proc = adapter.execute(ctx)
            raw = adapter.collect(ctx, proc)
            doc = adapter.normalize_result(raw, ctx)
            self.assertEqual(doc["measurements"]["latency_ms"], 12.5)
            self.assertTrue(doc["measurements"]["tests_passed"])


class CampaignIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        if not CLI.is_file():
            self.skipTest("scripts/run_campaign.py not present (Leaf A blocker)")
        self.campaign_dir = _prepare_campaign_copy()

    def tearDown(self) -> None:
        parent = self.campaign_dir.parent
        shutil.rmtree(parent, ignore_errors=True)

    def test_validate_baseline_trial_and_lock_mismatch(self) -> None:
        from campaign_runner.errors import LockMismatchError
        from campaign_runner.runner import run_baseline, run_trial, validate_campaign

        validate_campaign(self.campaign_dir)
        proc = _run_cli(["validate", str(self.campaign_dir)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

        baseline = run_baseline(self.campaign_dir)
        self.assertEqual(baseline.get("evaluator_status"), "success")
        baseline_path = self.campaign_dir / "state" / "baseline.json"
        sealed = baseline_path.read_text(encoding="utf-8")
        self.assertIn('"sealed": true', sealed)
        # Evaluator import may create bytecode; fixture .gitignore covers it,
        # but remove any stray untracked noise before the next isolation check.
        shutil.rmtree(self.campaign_dir / "subject" / "__pycache__", ignore_errors=True)

        subject = self.campaign_dir / "subject" / "work.py"
        subject.write_text(
            '"""Improved candidate."""\n\nLATENCY_MS = 40\n\n\ndef ok() -> bool:\n    return True\n',
            encoding="utf-8",
        )
        _git(self.campaign_dir, "add", "subject/work.py")
        _git(self.campaign_dir, "commit", "-m", "improve latency")
        shutil.rmtree(self.campaign_dir / "subject" / "__pycache__", ignore_errors=True)

        ledger_before = (self.campaign_dir / "state" / "ledger.jsonl").read_text(
            encoding="utf-8"
        )
        trial_out = run_trial(self.campaign_dir, candidate_id="improved-latency")
        comparison = trial_out["comparison"]
        self.assertEqual(comparison["comparator_outcome"], "dominates")
        self.assertEqual(comparison["trial_outcome"], "accepted")
        self.assertTrue(comparison["advance_best"])
        ledger_after = (self.campaign_dir / "state" / "ledger.jsonl").read_text(
            encoding="utf-8"
        )
        self.assertGreater(len(ledger_after), len(ledger_before))
        self.assertIn("candidate_accepted", ledger_after)
        self.assertIn("best_advanced", ledger_after)

        # Tamper with a protected evaluator file, commit so dirty-check passes,
        # leave lock digests stale → lock mismatch abort.
        eval_run = self.campaign_dir / "eval" / "run.py"
        eval_run.write_text(
            eval_run.read_text(encoding="utf-8") + "\n# tampered\n",
            encoding="utf-8",
        )
        _git(self.campaign_dir, "add", "eval/run.py")
        _git(self.campaign_dir, "commit", "-m", "tamper evaluator")

        with self.assertRaises(LockMismatchError):
            run_trial(self.campaign_dir, candidate_id="tampered")

        proc_bad = _run_cli(
            ["trial", str(self.campaign_dir), "--candidate-id", "tampered-cli"]
        )
        self.assertNotEqual(proc_bad.returncode, 0, proc_bad.stdout + proc_bad.stderr)
        self.assertRegex(
            (proc_bad.stderr + proc_bad.stdout).lower(),
            r"digest mismatch|lock",
        )

    def test_runner_never_exposes_git_reset_hard(self) -> None:
        runner_pkg = SCRIPTS / "campaign_runner"
        offenders: list[str] = []
        for path in [CLI, *runner_pkg.rglob("*.py")]:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if "reset --hard" not in line:
                    continue
                # Allow comments/strings that forbid the practice.
                lowered = line.lower()
                if any(
                    token in lowered
                    for token in ("forbid", "never", "must not", "do not", "banned")
                ):
                    continue
                if line.lstrip().startswith("#"):
                    continue
                offenders.append(f"{path.relative_to(ROOT)}:{lineno}:{line.strip()}")
        self.assertEqual(offenders, [], msg="git reset --hard must not be invoked")


if __name__ == "__main__":
    unittest.main()
