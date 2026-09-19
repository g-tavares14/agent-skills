# AGENTS.md

Guidance for agents working **in this repository** (the Grok Build + Codex skills pack). Do not copy this file into application repos — those get their own `AGENTS.md`. The reusable assets are `skills/`, `agents/`, `commands/`, `hooks/`, and `references/`.

Code examples in skills and references are **TypeScript and Python only**.

## Layout

| Path | Role |
|------|------|
| `skills/<name>/SKILL.md` | Workflows (the *how*) |
| `agents/<role>.md` | Personas (the *who*) |
| `commands/*.md` | Grok slash commands (the *when*) |
| `hooks/hooks.json` | Grok plugin hook (`simplify-ignore`) |
| `references/` | Shared checklists cited by skills |
| `plugin.json` | Grok plugin manifest |
| `.grok-plugin/marketplace.json` | Grok marketplace index |
| `.codex-plugin/plugin.json` | Codex plugin manifest |
| `.agents/plugins/marketplace.json` | Codex marketplace catalog |

## Composition

- **Skills** are mandatory hops when an intent matches. Follow the steps; do not skip verification.
- **Personas do not invoke other personas.** Slash commands (or the user) orchestrate.
- The only multi-persona pattern this pack endorses is parallel fan-out with a merge step (`/agent-skills:ship`).
- On Grok, spawn personas with `spawn_subagent`. Prefer `code-reviewer`, then `agent-skills:code-reviewer`.

See [docs/agents.md](docs/agents.md) and [references/orchestration-patterns.md](references/orchestration-patterns.md).

## Editing this pack

- Keep skill frontmatter `name` and `description` specific — Grok and Codex use them for auto-invocation.
- Put long checklists in `references/`, not duplicated inside every skill.
- When you add a code example, use TypeScript or Python (or both).
- Frontend UI examples stay TypeScript/React (`tsx`).
- After changing packaging, run `grok plugin validate .`, `grok inspect`, and validate the Codex JSON manifests.

## Intent → skill

- New feature → `spec-driven-development`, then `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`
- Bug / failure → `debugging-and-error-recovery`
- Review → `code-review-and-quality`
- Refactor → `code-simplification`
- API / module boundary → `api-and-interface-design`
- UI → `frontend-ui-engineering`
