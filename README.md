# Agent Skills for Codex and Claude Code

Engineering workflows and reusable skills for **Codex CLI**, **Codex in the ChatGPT app**, and **Claude Code** (CLI, desktop, web, and IDE extensions). The main workflow has five steps: **spec → plan → build → verify → review**. Code examples use TypeScript and Python.

The package follows the portable Agent Plugins layout and uses the OpenAI plugin extension for Codex presentation and lifecycle hooks. For Claude Code it ships a `.claude-plugin/` manifest and marketplace. Both platforms load the same `skills/` directories and the same `hooks/hooks.json`.

## Install in Codex CLI

Run from a terminal with Codex CLI installed:

```bash
codex plugin marketplace add https://github.com/g-tavares14/agent-skills.git \
  --sparse .agents/plugins \
  --sparse plugin.json \
  --sparse skills \
  --sparse hooks \
  --sparse references \
  --sparse docs \
  --sparse README.md \
  --sparse LICENSE
codex plugin add agent-skills@gtavares-skills
codex plugin list --marketplace gtavares-skills
```

The repeated `--sparse` paths include the catalog and the root-level plugin files referenced by it.

## Install in the ChatGPT app

Open this repository in Codex. The app discovers the repository marketplace at `.agents/plugins/marketplace.json`. Open the Plugins Directory, select `gtavares-skills`, and install **Agent Skills**. Review and trust the bundled hook before using it; changed hook definitions require review again.

The hook requires Python 3. In Codex CLI, use `/hooks` to inspect and trust the hook. The hook checks `apply_patch` calls for edits to protected blocks and leaves source files untouched.

## Install in Claude Code

Inside a Claude Code session:

```text
/plugin marketplace add g-tavares14/agent-skills
/plugin install agent-skills@gtavares-skills
```

Or from a terminal:

```bash
claude plugin marketplace add g-tavares14/agent-skills
```

```bash
claude plugin install agent-skills@gtavares-skills
```

To try a local checkout without installing, start Claude Code with `claude --plugin-dir /path/to/agent-skills`.

Skills are namespaced by the plugin: the lifecycle shortcuts are `/agent-skills:spec`, `/agent-skills:plan`, `/agent-skills:build`, `/agent-skills:verify`, and `/agent-skills:review`. They only run when you invoke them; the other skills are also picked up automatically when a task matches their description. The bundled hook (Python 3) checks `Edit`, `MultiEdit`, and `Write` calls for changes to protected blocks.

## Five-step workflow

| Stage | Codex | Claude Code | Canonical workflow |
|---|---|---|---|
| Specify | `$spec` | `/agent-skills:spec` | `spec-driven-development` |
| Plan | `$plan` | `/agent-skills:plan` | `planning-and-task-breakdown` |
| Build | `$build` | `/agent-skills:build` | `incremental-implementation` + `test-driven-development` |
| Verify | `$verify` | `/agent-skills:verify` | Acceptance criteria and repository checks |
| Review | `$review` | `/agent-skills:review` | `code-review-and-quality` plus applicable security, test, and performance checks |

The complete cycle is spec → plan → build → verify → review. Invoke other specialized skills by their canonical names when the task calls for them.

## Skills and support files

| Path | Purpose |
|---|---|
| `skills/` | Workflow skills and the five explicit lifecycle shortcuts |
| `hooks/hooks.json` | `PreToolUse` hooks for protected code blocks (Codex and Claude Code) |
| `hooks/simplify_ignore_guard.py` | Read-only patch guard; does not rewrite source files |
| `references/` | Reusable checklists and guidance |
| `docs/` | Codex workflow and specialist guidance |
| `plugin.json` | Portable plugin manifest and OpenAI extension |
| `.agents/plugins/marketplace.json` | Repository marketplace for the ChatGPT app |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `.claude-plugin/marketplace.json` | Claude Code marketplace |

## Validate local changes

```bash
python3 -m json.tool plugin.json
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool .claude-plugin/plugin.json
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool hooks/hooks.json
python3 -m unittest discover -s hooks -p 'test_*.py'
python3 -m py_compile hooks/simplify_ignore_guard.py
```

MIT. Upstream copyright: Addy Osmani. See [LICENSE](LICENSE).
