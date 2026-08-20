# Writing an Agent Note

1. Read [.agents/notes/README.md](../../.agents/notes/README.md).
2. Search `.agents/notes/` for an existing owner of the decision. Update it if the decision is the same.
3. Pick lifecycle (`proposed`, `implemented`, `rejected`) and class (`feature`, `bug-fix`, `simplification`, `architecture`, `process`, `testing`).
4. Create `.agents/notes/{lifecycle}/{class}/yyyy-mm-dd-slug.md` with the header block and required sections for that lifecycle.
5. Record real alternatives that lost. Do not invent them.
6. Run `python scripts/verify_template.py`.
