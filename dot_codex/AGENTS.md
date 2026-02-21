# Agent Instructions

- Use Conventional Commits for all commit messages (e.g., `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`).
- When committing, include a body that explains both the motivation (why) and the concrete change (what/how) so the change is understandable without reading the diff.

## Commit Message Body Style

- Prefer **2 or 3 short sentences** of prose, then a **small bullet list** of concrete changes.
- Start the prose with a short **diagnosis** of the previous state, e.g. "Previously this was implemented with X; this commit changes it to Y".
- Bullet points should be implementation-oriented (what changed) and reference key concepts/paths/flags when helpful.
- The whole commit should be wrapped at 72 columns.

Example:

    feat: add X

    Previously we supported only Z; this commit adds X to improve Y.
    Keep behavior backwards compatible for existing Z.

    - Add `--x` flag and validate inputs
    - Update API client to include X in requests
    - Add unit tests for success and error cases

## Commit Safety Guardrails

- Never use `git commit -m "..."` for multi-line messages or commit
  text containing backticks/code spans.
- Use this exact, copy/paste-safe pattern for commit messages
  (prevents shell interpolation in zsh/bash):

```bash
git commit -F - <<'EOF'
type: short subject

Previously X behaved like A; this commit changes it to B for reason C.
Keep compatibility for existing callers where possible.

- Add `path/to/file` changes for behavior B
- Update tests for edge case D and regression E
EOF
```

- Interpolation pitfall example (DO NOT USE):
  - `git commit -m "fix: msg" -m "- Add \`index.js\` and \`test:coverage\`"`
  - In this form, backticks can execute commands and strip text.
- After every commit and before push, verify author/committer and full
  message:
  - `git show -s --format='%H%n%an <%ae>%n%cn <%ce>%n%n%B' HEAD`
- If content is wrong, amend before pushing.

## Subagents

Use subagents eagerly for well-defined tasks with clear scope that are
good candidates for delegation.

Good candidates include:

- Detailed code investigation that requires substantial code research,
  where the goal is a well-targeted answer to a specific question.
- Implementation of a standalone module with no overlap with other
  files.

Spawn one agent per concern, run in parallel. Remember to close each
subagent once its work is complete and you have no further tasks for it.
