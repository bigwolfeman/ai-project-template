#!/usr/bin/env python3
"""Verify agent-note and experiment layout. Exits non-zero on the first class of errors collected."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from verify_campaign import check_campaign_artifacts, check_optional_research_skills

NOTE_CLASSES = (
    "feature",
    "bug-fix",
    "simplification",
    "architecture",
    "process",
    "testing",
)
NOTE_LIFECYCLES = ("proposed", "implemented", "rejected", "archived")
SKIP_NOTE_NAMES = {"README.md", "AGENTS.md"}
NOTE_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
EXPERIMENT_NAME = NOTE_NAME
EXPERIMENT_SKIP = {"README.md", "AGENTS.md"}

PROPOSED_SECTIONS = (
    "## Problem",
    "## Proposal",
    "## Alternatives considered",
    "## Acceptance criteria",
    "## Risks",
)
IMPLEMENTED_SECTIONS = (
    "## Problem",
    "## Decision",
    "## Alternatives considered",
    "## Consequences",
)
IMPLEMENTED_FORBIDDEN = (
    "## Proposal",
    "## Plan",
    "## Migration plan",
    "## Acceptance criteria",
)
REJECTED_SECTIONS = ("## Problem", "## Proposal", "## Alternatives considered")
PLANNED_SECTIONS = ("## Question", "## Hypothesis", "## Predictions", "## Method")
COMPLETED_SECTIONS = (
    "## Question",
    "## Hypothesis",
    "## Predictions",
    "## Method",
    "## Results",
    "## Verdict",
    "## Updated hypothesis",
)


class Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)


def heading_present(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def section_has_body(text: str, heading: str) -> bool:
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE)
    if match is None:
        return False
    rest = text[match.end() :]
    next_h = re.search(r"^## ", rest, re.MULTILINE)
    body = rest[: next_h.start()] if next_h else rest
    stripped = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
    if not stripped:
        return False
    placeholders = {"…", "...", "TBD", "TODO", "(link)", "YYYY-MM-DD"}
    lines = [ln.strip() for ln in stripped.splitlines() if ln.strip()]
    return any(ln not in placeholders and not ln.startswith("<") for ln in lines)


def check_required_dirs(errors: Errors) -> None:
    required = [
        ROOT / "AGENTS.md",
        ROOT / "docs" / "AGENTS.md",
        ROOT / "docs" / "constitution.md",
        ROOT / "docs" / "experiments" / "AGENTS.md",
        ROOT / ".agents" / "notes" / "README.md",
        ROOT / "scripts" / "verify_template.py",
    ]
    for path in required:
        if not path.is_file():
            errors.add(f"missing required file: {path.relative_to(ROOT)}")
    for lifecycle in NOTE_LIFECYCLES:
        for kind in NOTE_CLASSES:
            directory = ROOT / ".agents" / "notes" / lifecycle / kind
            if not directory.is_dir():
                errors.add(f"missing note class directory: {directory.relative_to(ROOT)}")
    for name in ("algorithms", "planned", "successes", "failures", "results", "templates"):
        directory = ROOT / "docs" / "experiments" / name
        if not directory.is_dir():
            errors.add(f"missing experiments directory: {directory.relative_to(ROOT)}")


def check_agent_notes(errors: Errors) -> None:
    notes_root = ROOT / ".agents" / "notes"
    for markdown in notes_root.rglob("*.md"):
        if markdown.name in SKIP_NOTE_NAMES:
            continue
        rel = markdown.relative_to(notes_root)
        parts = rel.parts
        if len(parts) != 3:
            errors.add(f"agent note must live at lifecycle/class/file.md: {rel}")
            continue
        lifecycle, kind, name = parts
        if lifecycle not in NOTE_LIFECYCLES:
            errors.add(f"unknown note lifecycle: {rel}")
            continue
        if kind not in NOTE_CLASSES:
            errors.add(f"unknown note class: {rel}")
            continue
        if not NOTE_NAME.match(name):
            errors.add(f"note filename must be yyyy-mm-dd-slug.md: {rel}")
        text = markdown.read_text(encoding="utf-8")
        if not text.startswith("# Agent Note: "):
            errors.add(f"note must start with '# Agent Note: ': {rel}")
        status_line = ""
        for line in text.splitlines()[:8]:
            if line.startswith("Status:"):
                status_line = line
                break
        if not status_line:
            errors.add(f"missing Status: line: {rel}")
            continue
        if lifecycle == "proposed" and status_line != "Status: proposed":
            errors.add(f"proposed note Status must be 'Status: proposed': {rel}")
        elif lifecycle == "implemented" and status_line != "Status: implemented":
            errors.add(f"implemented note Status must be 'Status: implemented': {rel}")
        elif lifecycle == "archived":
            if status_line != "Status: implemented":
                errors.add(f"archived note Status must remain 'Status: implemented': {rel}")
            if "Archived:" not in text:
                errors.add(f"archived note missing Archived: date: {rel}")
        elif lifecycle == "rejected" and not status_line.startswith("Status: rejected — "):
            errors.add(f"rejected note Status must be 'Status: rejected — <why>': {rel}")
        if lifecycle == "proposed":
            required = PROPOSED_SECTIONS
            forbidden: tuple[str, ...] = ()
        elif lifecycle == "implemented":
            required = IMPLEMENTED_SECTIONS
            forbidden = IMPLEMENTED_FORBIDDEN
        elif lifecycle == "archived":
            required = IMPLEMENTED_SECTIONS
            forbidden = IMPLEMENTED_FORBIDDEN
        else:
            required = REJECTED_SECTIONS
            forbidden = ()
        for heading in required:
            if not heading_present(text, heading):
                errors.add(f"{rel} missing {heading}")
            elif not section_has_body(text, heading):
                errors.add(f"{rel} empty {heading}")
        for heading in forbidden:
            if heading_present(text, heading):
                errors.add(f"{rel} implemented/archived notes must not contain {heading}")


def check_experiments(errors: Errors) -> None:
    exp_root = ROOT / "docs" / "experiments"
    for lifecycle, expected_status in (
        ("planned", "Status: planned"),
        ("successes", "Status: success"),
        ("failures", "Status: failure"),
    ):
        folder = exp_root / lifecycle
        for markdown in folder.glob("*.md"):
            if markdown.name in EXPERIMENT_SKIP:
                continue
            rel = markdown.relative_to(ROOT)
            if not EXPERIMENT_NAME.match(markdown.name):
                errors.add(f"experiment filename must be yyyy-mm-dd-slug.md: {rel}")
            text = markdown.read_text(encoding="utf-8")
            if not text.startswith("# Experiment: "):
                errors.add(f"experiment must start with '# Experiment: ': {rel}")
            if expected_status not in text.splitlines()[:8]:
                errors.add(f"{rel} must include {expected_status} near the top")
            if lifecycle == "planned":
                if heading_present(text, "## Results"):
                    errors.add(f"planned experiment must not contain ## Results: {rel}")
                required = PLANNED_SECTIONS
            else:
                required = COMPLETED_SECTIONS
            for heading in required:
                if not heading_present(text, heading):
                    errors.add(f"{rel} missing {heading}")
                elif not section_has_body(text, heading):
                    errors.add(f"{rel} empty {heading}")
    algorithms = exp_root / "algorithms"
    for markdown in algorithms.glob("*.md"):
        if markdown.name in EXPERIMENT_SKIP:
            continue
        rel = markdown.relative_to(ROOT)
        if not EXPERIMENT_NAME.match(markdown.name):
            errors.add(f"algorithm filename must be yyyy-mm-dd-slug.md: {rel}")
        text = markdown.read_text(encoding="utf-8")
        if not text.startswith("# Algorithm: "):
            errors.add(f"algorithm must start with '# Algorithm: ': {rel}")


def main() -> int:
    errors = Errors()
    check_required_dirs(errors)
    check_agent_notes(errors)
    check_experiments(errors)
    check_campaign_artifacts(errors, ROOT)
    check_optional_research_skills(errors, ROOT)
    if errors.items:
        print("verify_template.py failed:", file=sys.stderr)
        for item in errors.items:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("verify_template.py: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
