# Prompt regression fixtures

Deterministic cases for research-skill decisions and forbidden actions.

Spec: `Incomplete/automated-research-system-spec.md` §14 and §23.4.

Each `*.json` case encodes:

- `id` — stable fixture name
- `required_decisions` — substrings a correct agent response must include (any match rules listed)
- `forbidden_in_good` — substrings that must not appear in a correct response
- `good_response` / `bad_response` — illustrative snippets for regression checks
- `checks` — named string rules applied by `tests/test_prompt_fixtures.py`

These fixtures do not grade model output with an LLM. They only run string and rule checks.
