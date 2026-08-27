# Agent Note: Campaign schemas under lab/

Status: implemented

## Problem

Campaign JSON Schema files lived at repository root `schemas/`. That path is not named in the repository layout and sits outside the lab execution plane where campaigns, templates, and runner projections belong.

## Decision

Move all campaign schema files to `lab/schemas/`. Update `scripts/campaign_schema.py`, `scripts/verify_campaign.py`, ledger validation, tests, `lab/AGENTS.md`, root `AGENTS.md`, `docs/AGENTS.md`, architecture note, and `run-campaign` skill links.

`SCHEMA_DIR` is `lab/schemas/` relative to the repository root. The runner resolves that directory from `campaign_schema.SCHEMA_DIR` and falls back to walking parents for `lab/schemas` or legacy `schemas`.

## Alternatives considered

- **`.agents/schemas/`** — rejected; schemas are campaign contracts, not agent skills or notes.
- **Keep root `schemas/`** — rejected; root layout should not accumulate lab-specific artifacts.

## Consequences

- New imports or docs must reference `lab/schemas/`, not `schemas/`.
- External clones that still expect root `schemas/` must update paths.
- Verification: `python scripts/verify_template.py` and `python -m unittest discover -s tests -q`.
