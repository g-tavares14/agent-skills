# AGENTS.md

Guidance for Codex and Claude Code working in this repository (`CLAUDE.md` imports this file). The package targets Codex CLI, Codex in the ChatGPT app, and Claude Code. Do not copy this file into application repositories; they need their own `AGENTS.md` / `CLAUDE.md`. The reusable assets are `skills/`, `hooks/`, `references/`, and `docs/`.

## Layout

| Path | Role |
|---|---|
| `skills/<name>/SKILL.md` | Codex workflows and reusable engineering skills |
| `skills/<name>/agents/openai.yaml` | Codex skill presentation and invocation policy |
| `hooks/hooks.json` | Lifecycle hook registration shared by Codex and Claude Code |
| `hooks/simplify_ignore_guard.py` | Protected block check for `apply_patch`, `Edit`, `MultiEdit`, and `Write` |
| `references/` | Shared checklists cited by skills |
| `docs/` | Package and workflow documentation |
| `plugin.json` | Portable Agent Plugins manifest |
| `.agents/plugins/marketplace.json` | Codex app repository marketplace |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `.claude-plugin/marketplace.json` | Claude Code marketplace |

## Workflow

The only lifecycle shortcuts are `$spec` → `$plan` → `$build` → `$verify` → `$review` (in Claude Code: `/agent-skills:spec` … `/agent-skills:review`). Shortcut skills set `disable-model-invocation: true` for Claude Code and `allow_implicit_invocation: false` in `agents/openai.yaml` for Codex; keep both in sync. Canonical engineering skills remain available by name for specialized work.

## Composition

- Skills are the workflow unit. Keep `SKILL.md` frontmatter `name` and `description` specific and concise.
- The five lifecycle shortcuts delegate to canonical skills; do not duplicate a canonical workflow in its shortcut.
- `$review` coordinates applicable security, test, and performance checks. Use subagents (Codex subagents or the Claude Code Agent tool) for independent read-only passes when available; otherwise do the passes in the current session.
- Keep examples in skills and references in TypeScript or Python. Frontend examples use TypeScript/React (`tsx`).

## Intent → skill

| Intent | Skill |
|---|---|
| New feature or unclear requirements | `$spec`, then `$plan`, `$build`, `$verify`, `$review` |
| Bug or failure | `debugging-and-error-recovery` |
| Review | `$review` / `code-review-and-quality` |
| Refactor | `code-simplification` |
| API or module boundary | `api-and-interface-design` |
| UI | `frontend-ui-engineering` |

## Editing this package

- Keep every skill self-contained or include its supporting resources inside the skill directory when they are required at runtime.
- Support Codex and Claude Code only, using each platform's documented plugin manifest and hook formats. Do not add other agent platforms' configuration or commands.
- Keep names and versions consistent across `plugin.json`, `.agents/plugins/marketplace.json`, `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json`.
- Keep skill text platform-neutral; when a platform detail matters, name both Codex and Claude Code.
- Do not make the hook modify, mask, cache, or restore source files. Protected block checks must fail closed when a patch cannot be analyzed.
- After changing packaging, validate JSON and run the hook unit tests:

  ```bash
  python3 -m json.tool plugin.json
  python3 -m json.tool .agents/plugins/marketplace.json
  python3 -m json.tool .claude-plugin/plugin.json
  python3 -m json.tool .claude-plugin/marketplace.json
  python3 -m json.tool hooks/hooks.json
  python3 -m unittest discover -s hooks -p 'test_*.py'
  ```
