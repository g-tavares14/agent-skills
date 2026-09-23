# AGENTS.md

Guidance for Codex working in this repository. The package targets Codex CLI and Codex in the ChatGPT app. Do not copy this file into application repositories; they need their own `AGENTS.md`. The reusable assets are `skills/`, `hooks/`, `references/`, and `docs/`.

## Layout

| Path | Role |
|---|---|
| `skills/<name>/SKILL.md` | Codex workflows and reusable engineering skills |
| `skills/<name>/agents/openai.yaml` | Skill presentation and invocation policy |
| `hooks/hooks.json` | Codex lifecycle hook registration |
| `hooks/simplify_ignore_guard.py` | Protected block check for `apply_patch` |
| `references/` | Shared checklists cited by skills |
| `docs/` | Package and workflow documentation |
| `plugin.json` | Portable Agent Plugins manifest |
| `.agents/plugins/marketplace.json` | Codex app repository marketplace |

## Workflow

The only lifecycle shortcuts are `$spec` → `$plan` → `$build` → `$verify` → `$review`. Canonical engineering skills remain available by name for specialized work.

## Composition

- Skills are the workflow unit. Keep `SKILL.md` frontmatter `name` and `description` specific and concise.
- The five lifecycle shortcuts delegate to canonical skills; do not duplicate a canonical workflow in its shortcut.
- `$review` coordinates applicable security, test, and performance checks. Use Codex subagents for independent read-only passes when available; otherwise do the passes in the current session.
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
- Use Codex-supported plugin manifest and hook formats. Do not add another agent platform's configuration or commands.
- Keep `plugin.json` and `.agents/plugins/marketplace.json` names and versions consistent.
- Do not make the hook modify, mask, cache, or restore source files. Protected block checks must fail closed when a patch cannot be analyzed.
- After changing packaging, validate JSON and run the hook unit tests:

  ```bash
  python3 -m json.tool plugin.json
  python3 -m json.tool .agents/plugins/marketplace.json
  python3 -m unittest discover -s hooks -p 'test_*.py'
  ```
