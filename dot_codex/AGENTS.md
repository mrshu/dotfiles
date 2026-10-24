# Agent Instructions

- Restate in your own words what you think my goal is, making every implicit detail explicit. Then respond.
- Before adding complexity for a speculative or vanishingly unlikely race or security edge case, explain the concrete failure mode, likelihood, and complexity cost to me and get my buy-in. Do not silently expand scope for theoretical robustness.
- Use Conventional Commits for all commit messages (e.g., `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`).
- When committing, include a body that explains both the motivation (why) and the concrete change (what/how) so the change is understandable without reading the diff.

## Doors

- **Two-way door:** a decision you can walk back: code, branches, PRs, test data, dev infra...
- **One-way door:** one you can't: prod data, deploys to users, force-pushing a shared branch, deleting what you didn't make (always look before you delete to make sure), a message sent to another person...
- **Rubber stamp:** a question whose only sensible answer is yes, like "Want me to commit this?" Asking it costs me a round trip and teaches nothing.

Walk through two-way doors and show me after. Stop at one-way doors. Don't ask rubber stamps. If running something could answer the question, run it instead. Save questions for taste and product calls only I can make: one at a time, with your recommendation, using your harness's built-in question tool. No is an acceptable answer to me too.

Once I open a one-way door, it stays open for that work, including for any subagent you hand it to (quote me). Come back only if the door turns out to be different from the one I opened: more at stake than I was told, a check failing, something I didn't know about.

## Commit-to-Diff Fidelity

- Commit messages must describe the staged diff first, not just the
  discussion that led to it.
- Do not claim files, behaviors, or removals that are not present in
  the commit.
- If discussion context is important, include it as motivation, but tie
  it directly to concrete changes in the diff.
- Before committing, check `git diff --staged --name-only` and
  `git diff --staged` and ensure the message matches exactly.

## Commit Message Body Style

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

## GitHub Comments

- Never use MCP or connector tools to create, update, or send GitHub comments.
- Use the `gh` CLI instead when a GitHub comment needs to be posted.
