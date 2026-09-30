# AGENTS.md

Guidance for Claude Code working in this repository (`CLAUDE.md` imports this file). The package is a Claude Code plugin. Do not copy this file into application repositories; they need their own `AGENTS.md` / `CLAUDE.md`. The reusable assets are `catalog/`, `hooks/`, and `docs/`. Catalog skills are not loaded globally; they are copied into each application repository, which then owns and adapts its copy.

## Layout

| Path | Role |
|---|---|
| `skills/setup-project/` | The only skill loaded globally by the plugin; its script copies catalog skills into a project |
| `catalog/skills/<name>/SKILL.md` | Reusable engineering skills and the lifecycle shortcuts, one flat directory (README groups them by lifecycle phase) |
| `catalog/core.txt` | Skills every project gets |
| `catalog/agents/` | `implementer` and `reviewer` agent templates copied by `install` |
| `catalog/templates/` | `AGENTS.md` and `CLAUDE.md` templates copied by `install` when a project has none |
| `catalog/references/` | Shared checklists cited by skills (`../../references/` from a skill) |
| `hooks/hooks.json` | `SessionStart` and `PreToolUse` hook registration |
| `hooks/project_status.py` | Session start notice when a git repository is not set up |
| `hooks/agent_bash_guard.py` | Bash rules for the `implementer` and `reviewer` agents (subagent calls only) |
| `hooks/simplify_ignore_guard.py` | Protected block check for `Edit`, `MultiEdit`, and `Write` |
| `docs/` | Package and workflow documentation |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace |

## Workflow

The only lifecycle shortcuts are `/spec` → `/plan` → `/build` → `/verify` → `/review`. Catalog skills only run as project skills, so the catalog writes them without a plugin prefix; the only plugin-namespaced command is `/agent-skills:setup-project`. Shortcut skills set `disable-model-invocation: true`. Canonical engineering skills remain available by name for specialized work.

## Composition

- Skills are the workflow unit. Keep `SKILL.md` frontmatter `name` and `description` specific and concise.
- The five lifecycle shortcuts delegate to canonical skills; do not duplicate a canonical workflow in its shortcut.
- `/review` coordinates applicable security, test, and performance checks. Use subagents (the Agent tool) for independent read-only passes when available; otherwise do the passes in the current session.
- Keep examples in skills and references in TypeScript or Python. Frontend examples use TypeScript/React (`tsx`).

## Intent → skill

| Intent | Skill |
|---|---|
| New feature or unclear requirements | `/spec`, then `/plan`, `/build`, `/verify`, `/review` |
| Bug or failure | `debugging-and-error-recovery` |
| Review | `/review` / `code-review-and-quality` |
| Refactor | `code-simplification` |
| API or module boundary | `api-and-interface-design` |
| UI | `frontend-ui-engineering` |

## Editing this package

- Keep every skill self-contained or include its supporting resources inside the skill directory when they are required at runtime.
- Relative links must resolve both in the catalog (`catalog/skills/<skill>/`) and in a project (`.claude/skills/<skill>/`, references in `.claude/references/`): cite shared checklists as `../../references/<file>.md` and other skills as `../<skill>/SKILL.md`. A linked skill is copied along with the one that links to it, so link only what the skill needs at runtime; otherwise cite it by name.
- Add skills under `catalog/skills/`, never the root `skills/` (that would load them globally), and list them in the README under their lifecycle phase. Run the setup-project tests: they check that catalog links resolve, that core skills exist, and that agents only preload core skills.
- Target Claude Code only, using its documented plugin manifest and hook formats. Do not add other agent platforms' configuration.
- Keep names and versions consistent across `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Do not make hooks modify, mask, cache, or restore source files. Protected block checks and the agent Bash guard must fail closed when an input cannot be analyzed; the session start notice is advisory and stays silent on errors.
- Keep the agent Bash guard in step with the "Forbidden" sections of `catalog/agents/implementer.md` and `catalog/agents/reviewer.md`.
- After changing packaging, validate JSON and run the tests:

  ```bash
  python3 -m json.tool .claude-plugin/plugin.json
  python3 -m json.tool .claude-plugin/marketplace.json
  python3 -m json.tool hooks/hooks.json
  python3 -m unittest discover -s hooks -p 'test_*.py'
  python3 -m unittest discover -s skills/setup-project/scripts -p 'test_*.py'
  ```
