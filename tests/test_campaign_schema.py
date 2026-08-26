"""Schema and YAML-subset tests. Stdlib unittest only."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from campaign_schema import SchemaStore, load_document, validate_instance  # noqa: E402
from verify_campaign import STAGNATION_LIMITS, TOTAL_LIMITS, _check_budget  # noqa: E402
from yaml_subset import YamlError, load_yaml  # noqa: E402

TEMPLATE = ROOT / "lab" / "templates" / "campaign"
SCHEMAS = ROOT / "schemas"


class Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)


class YamlSubsetTests(unittest.TestCase):
    def test_mapping_and_nested_list(self) -> None:
        data = load_yaml(
            "\n".join(
                [
                    "title: Example",
                    "items:",
                    "  - name: tests_passed",
                    '    unit: "1"',
                    "    valid_range:",
                    "      min: 0",
                    "      max: 1",
                    "  - name: latency_ms",
                    "    unit: millisecond",
                    "flag: true",
                    "count: 3",
                    "empty: []",
                ]
            )
        )
        self.assertEqual(data["title"], "Example")
        self.assertEqual(data["items"][0]["name"], "tests_passed")
        self.assertEqual(data["items"][0]["valid_range"]["max"], 1)
        self.assertEqual(data["items"][1]["unit"], "millisecond")
        self.assertTrue(data["flag"])
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["empty"], [])

    def test_duplicate_key_fails(self) -> None:
        with self.assertRaises(YamlError) as ctx:
            load_yaml("a: 1\na: 2")
        self.assertIn("duplicate key", str(ctx.exception))


class CampaignSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.store = SchemaStore(SCHEMAS)
        cls.campaign_schema = cls.store.load(SCHEMAS / "campaign.schema.json")
        cls.manifest = load_document(TEMPLATE / "campaign.yaml")
        cls.state_schema = cls.store.load(SCHEMAS / "campaign-state.schema.json")
        cls.result_schema = cls.store.load(SCHEMAS / "evaluator-result.schema.json")

    def test_template_manifest_valid(self) -> None:
        errors = validate_instance(
            self.manifest,
            self.campaign_schema,
            source="campaign.yaml",
            schema_path=SCHEMAS / "campaign.schema.json",
            store=self.store,
        )
        self.assertEqual(errors, [])

    def test_unknown_field_names_field(self) -> None:
        bad = copy.deepcopy(self.manifest)
        bad["unexpected_flag"] = True
        errors = validate_instance(
            bad,
            self.campaign_schema,
            source="campaign.yaml",
            schema_path=SCHEMAS / "campaign.schema.json",
            store=self.store,
        )
        self.assertTrue(any("unexpected_flag" in item and "unknown field" in item for item in errors), errors)

    def test_missing_title_names_field(self) -> None:
        bad = copy.deepcopy(self.manifest)
        del bad["title"]
        errors = validate_instance(
            bad,
            self.campaign_schema,
            source="campaign.yaml",
            schema_path=SCHEMAS / "campaign.schema.json",
            store=self.store,
        )
        self.assertTrue(any("title" in item and "missing required field" in item for item in errors), errors)

    def test_invalid_campaign_state(self) -> None:
        doc = {
            "schema_version": "1.0.0",
            "campaign_id": "example-generic-command",
            "state": "never-stop",
            "updated_at": "2026-08-24T00:00:00Z",
        }
        errors = validate_instance(
            doc,
            self.state_schema,
            source="state/campaign.json",
            schema_path=SCHEMAS / "campaign-state.schema.json",
            store=self.store,
        )
        self.assertTrue(any("state" in item and "never-stop" in item for item in errors), errors)

    def test_budget_without_stagnation_fails(self) -> None:
        collector = Errors()
        _check_budget({"resource_budget": {"max_trial_count": 3}}, "campaign.yaml", collector)
        self.assertTrue(any("stagnation" in item for item in collector.items), collector.items)
        self.assertTrue(any("resource_budget" in item for item in collector.items), collector.items)

    def test_budget_requires_total_limit(self) -> None:
        collector = Errors()
        _check_budget({"resource_budget": {"max_stagnation_trials": 4}}, "campaign.yaml", collector)
        self.assertTrue(any("total campaign limit" in item for item in collector.items), collector.items)
        self.assertTrue(set(TOTAL_LIMITS) and set(STAGNATION_LIMITS))

    def test_evaluator_result_schema_rejects_bad_outcome(self) -> None:
        digest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        doc = {
            "schema_version": "1.0.0",
            "campaign_id": "example-generic-command",
            "trial_id": "trial-1",
            "candidate_id": "abc",
            "evaluator_digest": digest,
            "protocol_digest": digest,
            "environment_digest": digest,
            "started_at": "2026-08-24T00:00:00Z",
            "ended_at": "2026-08-24T00:00:01Z",
            "measurements": {"tests_passed": True},
            "hard_constraint_results": [{"name": "tests_pass", "passed": True}],
            "runtime_resource_use": {"wall_clock_seconds": 0.2},
            "artifact_references": [],
            "evaluator_status": "success",
            "diagnostic_messages": [],
            "trial_outcome": "ship-it",
        }
        errors = validate_instance(
            doc,
            self.result_schema,
            source="result.json",
            schema_path=SCHEMAS / "evaluator-result.schema.json",
            store=self.store,
        )
        self.assertTrue(any("trial_outcome" in item and "ship-it" in item for item in errors), errors)

    def test_lock_and_state_files_are_json(self) -> None:
        for name in (
            "evaluator.lock.json",
            "state/campaign.json",
            "state/baseline.json",
            "state/best.json",
        ):
            json.loads((TEMPLATE / name).read_text(encoding="utf-8"))


class IsolatedCampaignDirTests(unittest.TestCase):
    def test_validate_file_reports_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "campaign.yaml"
            path.write_text("schema_version: \"1.0.0\"\n", encoding="utf-8")
            from campaign_schema import validate_file

            errors = validate_file(path, SCHEMAS / "campaign.schema.json")
            self.assertTrue(errors)
            self.assertTrue(any("campaign_id" in item or "title" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
