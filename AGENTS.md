# AGENTS.md

Guidance for agents working **in this repository** (the skills pack). Do not copy this file into application repos — those get their own `AGENTS.md`. The reusable assets are `skills/`, `agents/`, `commands/`, `.agents/skills/`, `hooks/`, and `references/`.

Code examples in skills and references are **TypeScript and Python only**.

## Layout

| Path | Role |
|------|------|
| `skills/<name>/SKILL.md` | Workflows (the *how*) |
| `agents/<role>.md` | Personas (the *who*) |
| `commands/*.md` | Grok slash commands (the *when*) |
| `.agents/skills/` | Zed / Zed Delta skills: symlinks to `skills/` plus lifecycle wrappers |
| `hooks/hooks.json` | Grok plugin hook (`simplify-ignore`) |
| `references/` | Shared checklists cited by skills |
| `plugin.json` | Grok plugin manifest |
| `.grok-plugin/marketplace.json` | Marketplace index |
| `.grok/{skills,agents}` | Symlinks so Grok discovers skills/personas when this repo is the cwd |
| `scripts/install-grok.sh` | Install + enable this plugin as the Grok machine default |
| `scripts/install-zed.sh` | Machine default for Zed/Delta: `~/.agents/skills/` plus personal `AGENTS.md` |

## Composition

- **Skills** are mandatory hops when an intent matches. Follow the steps; do not skip verification.
- **Personas do not invoke other personas.** Slash commands (or the user) orchestrate.
- The only multi-persona pattern this pack endorses is parallel fan-out with a merge step (`/agent-skills:ship` on Grok, `/ship` on Zed/Delta).
- **Grok:** spawn personas with `spawn_subagent`. Prefer `code-reviewer`, then `agent-skills:code-reviewer`.
- **Zed:** `spawn_agent`; prepend `<pack-root>/agents/<role>.md`.
- **Zed Delta:** Worker / Scout / Reviewer profiles — not custom types from `agents/*.md`. Prepend the persona file. Pack review is `/code-review`, not Delta's built-in `/review`.

See [docs/agents.md](docs/agents.md) and [references/orchestration-patterns.md](references/orchestration-patterns.md).

## Editing this pack

- Keep skill frontmatter `name` and `description` specific — Grok and Zed use them for auto-invocation.
- Lifecycle wrappers under `.agents/skills/{spec,plan,build,test,constraints,code-review,code-simplify,webperf,ship}/` stay `disable-model-invocation: true`.
- Zed is flat-only: every skill must be a direct child of `.agents/skills/`. Do not nest categories.
- Put long checklists in `references/`, not duplicated inside every skill.
- When you add a code example, use TypeScript or Python (or both).
- Frontend UI examples stay TypeScript/React (`tsx`).
- After changing Grok packaging, run `./scripts/install-grok.sh` (or `grok plugin validate .` and `grok inspect`).
- After changing `.agents/skills/` or the default Zed/Delta instructions, run `./scripts/install-zed.sh`. That writes a managed block into personal `AGENTS.md` (`~/.config/zed/AGENTS.md`, `~/.config/delta/AGENTS.md`, …) — it does not copy this file. This `AGENTS.md` stays pack-repo-only.

Grok also scans `.agents/skills/` (this repo and `~/.agents/skills`). The installers add those paths to `[skills].ignore` in `~/.grok/config.toml` so Grok keeps using the plugin instead of loading the Zed copies twice.

## Intent → skill

- New feature → `spec-driven-development`, then `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`
- Bug / failure → `debugging-and-error-recovery`
- Review → `code-review-and-quality`
- Refactor → `code-simplification`
- API / module boundary → `api-and-interface-design`
- UI → `frontend-ui-engineering`
