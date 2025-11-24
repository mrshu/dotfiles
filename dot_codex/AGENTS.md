# Global Codex instructions

## Git commit messages
- Subject: lower-case scope, colon, short imperative summary (max ~65 chars). Example: `ghostty: add blood moon theme and tmux passthrough`
- Body: hyphen bullets, one line each, no blank lines between bullets. Use present/imperative voice.
- Never leave blank lines between bullet lines in the body; remove any that editors or tools insert.
- Leave exactly one blank line between subject and body. Omit body if truly unnecessary.
- Keep scope meaningful (tool/app or area); prefer shorter scopes to wide ones.
- Do not auto-wrap; keep lines under ~72 chars.

## When unsure
- Ask before inventing a scope.
- Follow existing log style in the repo if it conflicts; otherwise use the above.

## Apply/commit
- Stage only intended files; never auto-revert user changes.
- If commit fails validation, surface the reason and align with these rules.
