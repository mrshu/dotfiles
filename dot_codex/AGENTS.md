# Agent Instructions

- Use Conventional Commits for all commit messages (e.g., `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`).
- When committing, include a body that explains both the motivation (why) and the concrete change (what/how) so the change is understandable without reading the diff.

## Commit Message Body Style

- Prefer **2 short sentences** of prose, then a **small bullet list** of concrete changes.
- Start the prose with a short **diagnosis** of the previous state, e.g. "Previously this was implemented with X; this commit changes it to Y".
- Bullet points should be implementation-oriented (what changed) and reference key concepts/paths/flags when helpful.

Example:

    feat: add X

    Previously we supported only Z; this commit adds X to improve Y.
    Keep behavior backwards compatible for existing Z.

    - Add `--x` flag and validate inputs
    - Update API client to include X in requests
    - Add unit tests for success and error cases
