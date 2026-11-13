# dotfiles


## Install

    $ pip install pipx
    $ pipx install pyinfra

And now install the standard tools:
    $ pyinfra @local install.py

On macOS, Alacritty comes directly from its official GitHub releases.
The installer checks GitHub's release metadata for the latest stable version,
verifies the disk image against the upstream SHA256 digest, and installs the
app, command, terminfo, manuals and shell completions. It keeps quarantine so
macOS approval remains explicit. On first launch, use System Settings > Privacy
& Security > Open Anyway if macOS asks for approval.

Quit Alacritty before installing or updating it. The pyinfra deployment stages
and checks the new app before removing any old Homebrew cask, and keeps a backup
during replacement. Settings are preserved. Use the dotfiles installer for both
initial setup and updates:

    $ pyinfra @local install.py

To preview the deployment without changing files:

    $ pyinfra @local install.py --dry

The Alacritty helper runs as part of this deployment. No separate command is
needed.

Flameshot uses its official
[`flameshot-org/flameshot`](https://github.com/flameshot-org/homebrew-flameshot)
tap. Its replacement is fetched and checked before the old cask is removed.
Only this cask is trusted, and `--zap` is never used. Use `brew update` and
`brew upgrade` for future Flameshot updates. Flameshot is skipped on macOS
versions older than 15 and may need the same first-launch approval.

On Linux, both apps continue to come from DNF.

## OMP settings

Chezmoi manages OMP preferences for the default agent and all current named
profiles: `bare`, `codex`, `commandc`, `commandcode`, `gpt`, and `rc`.

`.chezmoitemplates/omp-config.yml.tmpl` defines the standard models, UI, and
feature settings. Each profile uses this template and supplies only its
overrides. Shared settings apply first, followed by profile overrides.
Other local keys in each `config.yml` are preserved.

Apply only these settings from this checkout:

```sh
chezmoi --source "$PWD" apply --parent-dirs ~/.omp
```

For a new profile, copy
`dot_omp/private_profiles/private_codex/private_agent/modify_private_config.yml`
to the matching `private_<name>/private_agent/` directory. That file uses the
standard setup without overrides. Apply chezmoi again to create its config.
OMP itself does not inherit settings between profiles.

Every profile gets three model presets. Each one snapshots every role, so
switching never silently clears one:

- `commandcode` — deepseek v4.1 flash `default`, flash-fast `smol`, v4-pro
  `slow`, GPT-6.1 Terra `advisor`, all via `commandcode-alpha`. Cheap tiers
  carry the token volume ($0.15–$0.16 per 1M input); the $0.66–$1.00 tiers
  are reserved for `slow` and `advisor`.
- `claude` — Opus 5.5 `default`, Sonnet 5.5 `smol`/`slow` via `anthropic`,
  GPT-6.1 Sol `advisor` via `openai-codex`.
- `openai` — GPT-6.1 Sol `default`, Terra `smol`/`slow` via `openai-codex`,
  Claude Fable 5.2 `advisor` via `anthropic`.

`judge` stays on `commandcode/typesafe/jev` in all three. The global config
additionally pins `modelRoles.default` to deepseek v4.1 flash, so new
sessions start there without switching a preset.

Credentials, sessions, databases, caches, plugin installs, and generated
extensions stay local. Setup markers, AutoQA consent, and Codex redemption
choices are also local and are preserved when settings are applied.

## Agent skills

`npx skills add … -g` owns `~/.agents/skills/<name>/` and the symlinks in
`~/.claude/skills/`. chezmoi does not manage those files; it records *which*
global skills a machine should have.

- `.chezmoidata.json` → `agentSkills.repos` maps each source repo to the
  skills installed from it (currently 21 skills from 9 repos).
- `.chezmoiscripts/run_onchange_after_50_agent_skills.sh.tmpl` installs any
  skill that is missing, via
  `npx skills add <repo> --skill <name> -g -y -a claude-code -a cursor`.
  It re-runs only when its rendered content changes, and skips skills already
  present without touching the network.

There is no lockfile-based restore for global scope
([#283](https://github.com/vercel-labs/skills/issues/283),
[#549](https://github.com/vercel-labs/skills/issues/549)):
`experimental_install` only reads the project `skills-lock.json` and rejects
the v3 global lock, so the manifest above is the source of truth.

- New skill: `npx skills add <repo> -s <name> -g`, then add the name to the
  manifest and run `chezmoi apply`.
- Update: `npx skills update -g`.
- Do not `chezmoi add ~/.agents/skills`; the CLI rewrites those files.
