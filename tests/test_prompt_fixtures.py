"""Deterministic prompt-regression fixtures and skill-text guards.

Loads tests/prompt_fixtures/*.json and scans research skill docs for:
- refusal language for NEVER STOP / unbounded loops and git reset --hard
- absence of instructions that command git reset --hard as rejection
- at least three ## Example headings per skill references/examples.md

Fails loud with file paths. Stdlib unittest only.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "prompt_fixtures"
SKILLS_DIR = ROOT / ".agents" / "skills"

# Skills that must refuse unbounded / NEVER STOP language.
SKILLS_REQUIRE_UNBOUNDED_REFUSAL = frozenset(
    {
        "run-research-loop",
        "scope-research-campaign",
        "audit-research-integrity",
        "diagnose-failed-trial",
        "explore-performance-valley",
        "design-campaign",
    }
)

# Skills that must refuse destructive hard-reset as candidate rejection.
SKILLS_REQUIRE_HARD_RESET_REFUSAL = frozenset(
    {
        "run-research-loop",
        "scope-research-campaign",
        "evaluate-candidate",
        "explore-performance-valley",
        "promote-research-result",
        "audit-research-integrity",
        "diagnose-failed-trial",
        "manage-research-issues",
        "baseline-campaign",
        "design-campaign",
        "prove-property",
        "synthesize-campaign",
    }
)

UNBOUNDED_REFUSAL_RE = re.compile(
    r"(?is)("
    r"refuse[sd]?\s+[`'\"]?NEVER\s+STOP"
    r"|does\s+not\s+follow\s+[`'\"]?NEVER\s+STOP"
    r"|NEVER\s+STOP[`'\"]?\s+is\s+unbounded"
    r"|refuse[sd]?\s+.{0,80}unbounded"
    r"|unbounded\s+.{0,80}refuse"
    r"|refuse[sd]?\s+an?\s+unbounded"
    r"|refuse[sd]?\s+that\s+instruction"
    r")"
)

HARD_RESET_REFUSAL_RE = re.compile(
    r"(?is)("
    r"refuse[sd]?\s+.{0,120}git\s+reset\s+--hard"
    r"|git\s+reset\s+--hard.{0,120}refuse"
    r"|does\s+not\s+(?:run|use)\s+[`'\"]?git\s+reset\s+--hard"
    r"|do\s+not\s+(?:run|use)\s+[`'\"]?git\s+reset\s+--hard"
    r"|must\s+not\s+(?:run|use)\s+[`'\"]?git\s+reset\s+--hard"
    r"|forbidden[:\s].{0,40}git\s+reset\s+--hard"
    r"|git\s+reset\s+--hard.{0,80}(?:finding|forbidden)"
    r"|finding.{0,80}git\s+reset\s+--hard"
    r")"
)

# Imperative / agent-directed command to run hard reset (not a finding citation).
HARD_RESET_COMMAND_RE = re.compile(
    r"(?i)("
    r"the\s+agent\s+(?:must\s+|should\s+|shall\s+|will\s+)?"
    r"(?:run|runs|use|uses|execute|executes)\s+`?git\s+reset\s+--hard"
    r"|(?:^|[.!:;]\s*)(?:run|running|execute|use|using)\s+`?git\s+reset\s+--hard"
    r"|reset\s+hard\s+when\s+a\s+candidate"
    r"|ask(?:s|ed)?\s+.{0,40}git\s+reset\s+--hard"
    r"\s+to\s+(?:discard|reject|drop|hide)"
    r")"
)

HARD_RESET_SAFE_CONTEXT_RE = re.compile(
    r"(?i)("
    r"refuse|refuses|refused|forbidden|finding|findings|"
    r"does\s+not|do\s+not|must\s+not|never|"
    r"not\s+(?:run|use)|blocking|fail_abort|"
    r"is\s+a\s+finding|not\s+a\s+remediation|"
    r"campaign\s+used|ledger\s+`?reason|"
    r"searches?\s+.{0,60}git\s+reset|"
    r"checks?\s+.{0,60}git\s+reset|"
    r"rg\s+-n|"
    r"operator\s+asks"
    r")"
)

EXAMPLE_HEADING_RE = re.compile(r"^## Example\b", re.MULTILINE)
RESULTS_HEADING_RE = re.compile(r"^## Results\s*$", re.MULTILINE)
REQUIRED_FIXTURE_IDS = frozenset(
    {
        "refuse-never-stop",
        "refuse-git-reset-hard",
        "predictions-before-results",
        "trial-vs-hypothesis-verdict",
        "evaluator-digest-tamper-abort",
        "noisy-comparison-no-spurious-win",
    }
)


def load_fixtures() -> list[dict]:
    if not FIXTURES_DIR.is_dir():
        raise FileNotFoundError(f"missing fixtures directory: {FIXTURES_DIR}")
    fixtures: list[dict] = []
    for path in sorted(FIXTURES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{path}: fixture root must be an object")
        if "id" not in data:
            raise ValueError(f"{path}: missing id")
        data["_path"] = str(path)
        fixtures.append(data)
    return fixtures


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(n in text for n in needles)


def _contains_all(text: str, needles: list[str]) -> bool:
    return all(n in text for n in needles)


def apply_good_checks(fixture: dict, text: str) -> list[str]:
    """Return human-readable failures for a candidate good response."""
    checks = fixture.get("checks") or {}
    failures: list[str] = []
    path = fixture.get("_path", fixture.get("id", "<fixture>"))

    must_any = checks.get("good_must_contain_any")
    if must_any and not _contains_any(text, must_any):
        failures.append(
            f"{path}: good response missing any of {must_any!r}"
        )

    must = checks.get("good_must_contain")
    if must and not _contains_all(text, must):
        missing = [n for n in must if n not in text]
        failures.append(f"{path}: good response missing {missing!r}")

    for group in checks.get("good_must_contain_any_of_groups") or []:
        if not _contains_any(text, group):
            failures.append(
                f"{path}: good response missing any of group {group!r}"
            )

    must_not = list(checks.get("good_must_not_contain") or [])
    must_not.extend(fixture.get("forbidden_in_good") or [])
    for needle in must_not:
        if needle and needle in text:
            failures.append(
                f"{path}: good response must not contain {needle!r}"
            )

    return failures


def iter_skill_markdown() -> list[Path]:
    paths: list[Path] = []
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        paths.append(skill_md)
    for examples in sorted(SKILLS_DIR.glob("*/references/examples.md")):
        paths.append(examples)
    return paths


def research_skills_with_examples() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/references/examples.md"))


def line_commands_hard_reset(path: Path, text: str) -> list[str]:
    """Detect lines that instruct running git reset --hard as rejection."""
    failures: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "git reset --hard" not in line and "reset hard" not in line.lower():
            continue
        if HARD_RESET_SAFE_CONTEXT_RE.search(line):
            continue
        if HARD_RESET_COMMAND_RE.search(line):
            failures.append(
                f"{path}:{lineno}: commands git reset --hard as rejection "
                f"(refusal/forbidden/finding context required): {line.strip()!r}"
            )
    return failures


class PromptFixtureLoadTests(unittest.TestCase):
    def test_fixtures_directory_and_required_ids(self) -> None:
        self.assertTrue(
            FIXTURES_DIR.is_dir(),
            f"missing fixtures directory: {FIXTURES_DIR}",
        )
        fixtures = load_fixtures()
        self.assertTrue(fixtures, f"no JSON fixtures in {FIXTURES_DIR}")
        ids = {f["id"] for f in fixtures}
        missing = REQUIRED_FIXTURE_IDS - ids
        self.assertFalse(
            missing,
            f"missing required fixture ids: {sorted(missing)}",
        )

    def test_each_fixture_has_good_and_useful_structure(self) -> None:
        for fixture in load_fixtures():
            path = fixture["_path"]
            with self.subTest(fixture=fixture["id"]):
                self.assertIn("good_response", fixture, path)
                self.assertTrue(
                    str(fixture["good_response"]).strip(),
                    f"{path}: empty good_response",
                )
                self.assertIn("checks", fixture, path)
                self.assertIsInstance(fixture["checks"], dict, path)


class PromptFixtureRuleTests(unittest.TestCase):
    def test_good_responses_pass_checks(self) -> None:
        for fixture in load_fixtures():
            with self.subTest(fixture=fixture["id"]):
                failures = apply_good_checks(fixture, fixture["good_response"])
                self.assertEqual(
                    failures,
                    [],
                    "good_response failed its own checks:\n"
                    + "\n".join(failures),
                )

    def test_bad_responses_fail_good_checks_when_flagged(self) -> None:
        for fixture in load_fixtures():
            checks = fixture.get("checks") or {}
            if not checks.get("bad_must_not_pass_good_rules"):
                continue
            bad = fixture.get("bad_response")
            if not bad:
                self.fail(f"{fixture['_path']}: bad_must_not_pass_good_rules "
                          "set but bad_response missing")
            with self.subTest(fixture=fixture["id"]):
                failures = apply_good_checks(fixture, bad)
                self.assertTrue(
                    failures,
                    f"{fixture['_path']}: bad_response unexpectedly passed "
                    "good checks",
                )

    def test_predictions_before_results_sample_planned_files(self) -> None:
        fixture = next(
            f for f in load_fixtures() if f["id"] == "predictions-before-results"
        )
        good = fixture["sample_planned_good"]
        bad = fixture["sample_planned_bad"]
        self.assertIsNone(
            RESULTS_HEADING_RE.search(good),
            f"{fixture['_path']}: sample_planned_good must not contain ## Results",
        )
        self.assertIsNotNone(
            RESULTS_HEADING_RE.search(bad),
            f"{fixture['_path']}: sample_planned_bad must contain ## Results",
        )
        for heading in ("## Hypothesis", "## Predictions", "## Method"):
            present = re.search(
                rf"^{re.escape(heading)}\s*$",
                good,
                re.MULTILINE,
            )
            self.assertIsNotNone(
                present,
                f"{fixture['_path']}: sample_planned_good missing {heading}",
            )

    def test_trial_hypothesis_vocabularies_listed(self) -> None:
        fixture = next(
            f for f in load_fixtures() if f["id"] == "trial-vs-hypothesis-verdict"
        )
        vocab = (fixture.get("checks") or {}).get("vocabularies") or {}
        self.assertEqual(
            set(vocab.get("trial_outcomes") or []),
            {"accepted", "rejected", "invalid", "inconclusive", "crashed"},
            fixture["_path"],
        )
        self.assertEqual(
            set(vocab.get("hypothesis_verdicts") or []),
            {"supported", "falsified", "unresolved"},
            fixture["_path"],
        )


class SkillDocGuardTests(unittest.TestCase):
    def test_unbounded_refusal_in_relevant_skills(self) -> None:
        for skill in sorted(SKILLS_REQUIRE_UNBOUNDED_REFUSAL):
            path = SKILLS_DIR / skill / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing skill file: {path}")
            text = path.read_text(encoding="utf-8")
            # Prefer SKILL.md; also accept refusal in that skill's examples.
            examples = SKILLS_DIR / skill / "references" / "examples.md"
            blob = text
            if examples.is_file():
                blob = text + "\n" + examples.read_text(encoding="utf-8")
            self.assertRegex(
                blob,
                UNBOUNDED_REFUSAL_RE,
                f"{path}: missing refusal language for NEVER STOP / "
                "unbounded loops (also checked examples.md if present)",
            )

    def test_hard_reset_refusal_in_relevant_skills(self) -> None:
        for skill in sorted(SKILLS_REQUIRE_HARD_RESET_REFUSAL):
            path = SKILLS_DIR / skill / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing skill file: {path}")
            text = path.read_text(encoding="utf-8")
            examples = SKILLS_DIR / skill / "references" / "examples.md"
            blob = text
            if examples.is_file():
                blob = text + "\n" + examples.read_text(encoding="utf-8")
            self.assertRegex(
                blob,
                HARD_RESET_REFUSAL_RE,
                f"{path}: missing refusal language for git reset --hard",
            )

    def test_no_skill_commands_hard_reset_as_rejection(self) -> None:
        failures: list[str] = []
        for path in iter_skill_markdown():
            text = path.read_text(encoding="utf-8")
            failures.extend(line_commands_hard_reset(path, text))
        self.assertEqual(
            failures,
            [],
            "skill docs must not command git reset --hard as rejection:\n"
            + "\n".join(failures),
        )

    def test_research_skills_have_at_least_three_example_headings(self) -> None:
        examples_files = research_skills_with_examples()
        self.assertTrue(
            examples_files,
            f"no references/examples.md under {SKILLS_DIR}",
        )
        for path in examples_files:
            text = path.read_text(encoding="utf-8")
            count = len(EXAMPLE_HEADING_RE.findall(text))
            self.assertGreaterEqual(
                count,
                3,
                f"{path}: expected at least 3 '## Example' headings, found {count}",
            )


if __name__ == "__main__":
    unittest.main()
