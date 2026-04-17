# System-wide Claude Code Instructions

Restate the question in fully concrete terms, making every implicit detail explicit. Then answer."

## Code Review Principles

When reviewing code (PRs, diffs, or during `/review`), go beyond surface-level correctness:

1. **"Should this code exist?"** — Question whether the abstraction or layer is needed before checking its implementation. The best review comment is often "delete this."
2. **"What does the layer below actually do?"** — When code builds on a framework primitive, verify behavior in the actual configured backend/runtime, not the abstract API.
3. **"What happens on the fallback path?"** — Defensive `try/except` that swallows errors can be worse than crashing. If a dependency is required, fail loudly.
4. **"Is this redundancy useful?"** — Defense in depth only works if each layer is independently correct. A broken layer on top of a working one is dead code.
5. **"What does the rest of the codebase do?"** — Review diffs in context. Check if the same pattern is handled differently elsewhere. Cross-file inconsistencies reveal dead code.
6. **Treat `pragma: no cover` / `noqa` as review smells** — If a branch is acknowledged as unreachable, ask why it exists and what happens if it executes.

## Commit Messages

- Use Conventional Commits for all commit messages (e.g., `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`).
- When committing, include a body that explains both the motivation (why) and the concrete change (what/how) so the change is understandable without reading the diff.

### Commit Message Body Style

- Prefer **2 or 3 short sentences** of prose, then a **small bullet list** of concrete changes.
- Start the prose with a short **diagnosis** of the previous state, e.g. "Previously this was implemented with X; this commit changes it to Y".
- Bullet points should be implementation-oriented (what changed) and reference key concepts/paths/flags when helpful.
- The whole commit should be wrapped at 72 columns.
- The body should cover: the motivation or problem being solved, what the implementation does at a high level, key design decisions or trade-offs, and notable details (edge cases handled, files affected, things *not* changed).
- The body should give a reviewer or future reader enough context to understand the commit without reading the diff.

Example:

    feat: add X

    Previously we supported only Z; this commit adds X to improve Y.
    Keep behavior backwards compatible for existing Z.

    - Add `--x` flag and validate inputs
    - Update API client to include X in requests
    - Add unit tests for success and error cases

### Commit Safety Guardrails

- Never use `git commit -m "..."` for multi-line messages or commit text containing backticks/code spans.
- Use this exact, copy/paste-safe pattern for commit messages (prevents shell interpolation in zsh/bash):

```bash
git commit -F - <<'EOF'
type: short subject

Previously X behaved like A; this commit changes it to B for reason C.
Keep compatibility for existing callers where possible.

- Add `path/to/file` changes for behavior B
- Update tests for edge case D and regression E
EOF
```

- Interpolation pitfall (DO NOT USE): `git commit -m "fix: msg" -m "- Add \`index.js\`"` — backticks can execute commands and strip text.
