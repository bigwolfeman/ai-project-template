"""Static campaign layout and schema checks used by verify_template.py."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from campaign_ledger import check_ids_and_ledger, check_pointers, relerr
from campaign_schema import ROOT, SchemaError, SchemaStore, load_document, validate_file

TEMPLATE_FILES = (
    "program.md",
    "campaign.yaml",
    "evaluator.lock.json",
    "state/campaign.json",
    "state/baseline.json",
    "state/best.json",
    "state/ledger.jsonl",
    "state/hypotheses/README.md",
    "state/issues/README.md",
    "reports/README.md",
    "pointers/README.md",
)
SCHEMA_FILES = (
    "campaign.schema.json",
    "evaluator-result.schema.json",
    "evaluator.lock.schema.json",
    "ledger-event.schema.json",
    "campaign-state.schema.json",
    "baseline.schema.json",
    "best.schema.json",
    "defs.schema.json",
    "campaign-policies.schema.json",
)
TOTAL_LIMITS = (
    "max_wall_clock_seconds",
    "max_trial_count",
    "max_cost",
    "max_api_calls",
    "max_compute_seconds",
    "max_storage_bytes",
)
STAGNATION_LIMITS = (
    "max_consecutive_crashes",
    "max_consecutive_rejected",
    "max_stagnation_seconds",
    "max_stagnation_trials",
)
RESEARCH_SKILLS = (
    "research-shared",
    "maintain-docs",
    "run-experiment",
    "setup-campaign",
    "run-campaign",
    "close-campaign",
    "prove-property",
)
# Thin skills: SKILL.md required; references/examples.md optional.
THIN_RESEARCH_SKILLS = frozenset({"research-shared", "maintain-docs"})
PLANNED_LINK = re.compile(r"\[[^\]]+\]\([^)]*lab/experiments/planned/[^)]+\)")


def check_campaign_artifacts(errors: Any, root: Path = ROOT) -> None:
    for rel in (
        "lab/AGENTS.md",
        "lab/spikes",
        "lab/campaigns",
        "lab/schemas",
        "lab/templates/campaign",
    ):
        path = root / rel
        if rel.endswith(".md"):
            if not path.is_file():
                errors.add(f"missing required file: {rel}")
        elif not path.is_dir():
            errors.add(f"missing required directory: {rel}")
    for name in SCHEMA_FILES:
        path = root / "lab" / "schemas" / name
        if not path.is_file():
            errors.add(f"missing required file: lab/schemas/{name}")
    template = root / "lab" / "templates" / "campaign"
    if template.is_dir():
        _check_campaign_dir(template, errors, root=root)
    campaigns = root / "lab" / "campaigns"
    if not campaigns.is_dir():
        return
    for child in sorted(campaigns.iterdir()):
        if child.name in {"README.md", "templates"} or child.name.startswith("."):
            continue
        if child.is_dir() and (child / "campaign.yaml").is_file():
            _check_campaign_dir(child, errors, root=root)


def check_optional_research_skills(errors: Any, root: Path = ROOT) -> None:
    skills_root = root / ".agents" / "skills"
    catalog = skills_root / "README.md"
    if not catalog.is_file():
        errors.add("missing required file: .agents/skills/README.md")
    for name in RESEARCH_SKILLS:
        skill_md = skills_root / name / "SKILL.md"
        if not skill_md.is_file():
            errors.add(f"missing required file: .agents/skills/{name}/SKILL.md")
            continue
        if not skill_md.read_text(encoding="utf-8").strip():
            errors.add(f"{skill_md.relative_to(root)}: SKILL.md is empty")
        if name in THIN_RESEARCH_SKILLS:
            continue
        examples = skills_root / name / "references" / "examples.md"
        if not examples.is_file():
            errors.add(f"missing required file: .agents/skills/{name}/references/examples.md")


def _check_campaign_dir(campaign_dir: Path, errors: Any, *, root: Path) -> None:
    rel = campaign_dir.relative_to(root)
    for name in TEMPLATE_FILES:
        path = campaign_dir / name
        if not path.is_file():
            errors.add(f"missing required file: {rel}/{name}")
    manifest_path = campaign_dir / "campaign.yaml"
    if not manifest_path.is_file():
        return
    store = SchemaStore(root / "lab" / "schemas")
    _schema_file(manifest_path, "campaign.schema.json", store, errors, root)
    _schema_file(campaign_dir / "evaluator.lock.json", "evaluator.lock.schema.json", store, errors, root)
    _schema_file(campaign_dir / "state/campaign.json", "campaign-state.schema.json", store, errors, root)
    _schema_file(campaign_dir / "state/baseline.json", "baseline.schema.json", store, errors, root)
    _schema_file(campaign_dir / "state/best.json", "best.schema.json", store, errors, root)
    try:
        manifest = load_document(manifest_path)
    except (OSError, SchemaError, ValueError, json.JSONDecodeError) as exc:
        errors.add(f"{rel}/campaign.yaml: {exc}")
        return
    if not isinstance(manifest, dict):
        errors.add(f"{rel}/campaign.yaml: <root>: expected type object")
        return
    _check_budget(manifest, f"{rel}/campaign.yaml", errors)
    _check_overlap(manifest, f"{rel}/campaign.yaml", errors)
    _check_program(campaign_dir / "program.md", rel, errors)
    check_ids_and_ledger(campaign_dir, manifest.get("campaign_id"), store, errors, root)
    check_pointers(campaign_dir / "pointers", rel, errors)


def _schema_file(
    path: Path, schema_name: str, store: SchemaStore, errors: Any, root: Path
) -> None:
    if path.is_file():
        for item in validate_file(path, store.schema_dir / schema_name, store):
            errors.add(relerr(item, root))


def _check_budget(manifest: dict[str, Any], source: str, errors: Any) -> None:
    budget = manifest.get("resource_budget")
    if not isinstance(budget, dict):
        errors.add(f"{source}: resource_budget: missing required field")
        return
    if not any(budget.get(name) is not None for name in TOTAL_LIMITS):
        errors.add(
            f"{source}: resource_budget: at least one total campaign limit is required "
            f"({', '.join(TOTAL_LIMITS)})"
        )
    if not any(budget.get(name) is not None for name in STAGNATION_LIMITS):
        errors.add(
            f"{source}: resource_budget: at least one stagnation limit is required "
            f"({', '.join(STAGNATION_LIMITS)})"
        )


def _check_overlap(manifest: dict[str, Any], source: str, errors: Any) -> None:
    mutable = manifest.get("mutable_paths")
    protected = manifest.get("protected_paths")
    if isinstance(mutable, list) and isinstance(protected, list):
        overlap = sorted(set(mutable) & set(protected))
        if overlap:
            errors.add(f"{source}: mutable_paths: overlaps protected_paths ({overlap})")
    promo = manifest.get("promotion_policy")
    if isinstance(promo, dict) and promo.get("requires_human_review") is not True:
        errors.add(f"{source}: promotion_policy.requires_human_review: must be true")
    net = manifest.get("network_policy")
    if isinstance(net, dict) and net.get("mode") == "deny" and net.get("allowed_hosts"):
        errors.add(f"{source}: network_policy.allowed_hosts: must be empty when mode is deny")


def _check_program(path: Path, rel: Path, errors: Any) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if PLANNED_LINK.search(text) is None:
        errors.add(f"{rel}/program.md: missing link to lab/experiments/planned/")
    if re.search(r"^## Predictions\s*$", text, re.MULTILINE):
        errors.add(f"{rel}/program.md: must not copy ## Predictions")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: verify_campaign.py <campaign-dir>", file=sys.stderr)
        return 2
    campaign_dir = Path(args[0]).resolve()
    if not campaign_dir.is_dir():
        print(f"verify_campaign.py: missing directory {campaign_dir}", file=sys.stderr)
        return 1

    class Errors:
        def __init__(self) -> None:
            self.items: list[str] = []

        def add(self, message: str) -> None:
            self.items.append(message)

    errors = Errors()
    _check_campaign_dir(campaign_dir, errors, root=ROOT)
    if errors.items:
        print("verify_campaign.py failed:", file=sys.stderr)
        for item in errors.items:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("verify_campaign.py: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
