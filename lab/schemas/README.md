# Campaign JSON Schema

Draft 2020-12 schemas for the research campaign static contract and runner projections.

| File | Validates |
|---|---|
| `campaign.schema.json` | `campaign.yaml` manifest |
| `evaluator.lock.schema.json` | `evaluator.lock.json` |
| `evaluator-result.schema.json` | Evaluator output per trial |
| `ledger-event.schema.json` | One line of `state/ledger.jsonl` |
| `campaign-state.schema.json` | `state/campaign.json` |
| `baseline.schema.json` | `state/baseline.json` |
| `best.schema.json` | `state/best.json` |
| `defs.schema.json` | Shared `$defs` (referenced by other schemas) |
| `campaign-policies.schema.json` | Policy fragments referenced from the manifest |

Validation: `python scripts/verify_campaign.py lab/templates/campaign`. Implementation: `scripts/campaign_schema.py`.

Rules: [lab/AGENTS.md](../AGENTS.md).
