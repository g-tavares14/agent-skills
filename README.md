# Agent Skills for Codex

Engineering workflows and reusable skills for **Codex CLI** and **Codex in the ChatGPT app**. The main workflow has five steps: **spec → plan → build → verify → review**. Code examples use TypeScript and Python.

The package follows the portable Agent Plugins layout and uses the OpenAI plugin extension for Codex presentation and lifecycle hooks. Skills are regular `SKILL.md` directories.

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

## Five-step workflow

| Stage | Codex skill | Canonical workflow |
|---|---|---|
| Specify | `$spec` | `spec-driven-development` |
| Plan | `$plan` | `planning-and-task-breakdown` |
| Build | `$build` | `incremental-implementation` + `test-driven-development` |
| Verify | `$verify` | Acceptance criteria and repository checks |
| Review | `$review` | `code-review-and-quality` plus applicable security, test, and performance checks |

The complete cycle is `$spec` → `$plan` → `$build` → `$verify` → `$review`. Invoke other specialized skills by their canonical names when the task calls for them.

## Skills and support files

| Path | Purpose |
|---|---|
| `skills/` | Workflow skills and the five explicit lifecycle shortcuts |
| `hooks/hooks.json` | Codex `PreToolUse` hook for protected code blocks |
| `hooks/simplify_ignore_guard.py` | Read-only patch guard; does not rewrite source files |
| `references/` | Reusable checklists and guidance |
| `docs/` | Codex workflow and specialist guidance |
| `plugin.json` | Portable plugin manifest and OpenAI extension |
| `.agents/plugins/marketplace.json` | Repository marketplace for the ChatGPT app |

## Validate local changes

```bash
python3 -m json.tool plugin.json
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m unittest discover -s hooks -p 'test_*.py'
python3 -m py_compile hooks/simplify_ignore_guard.py
```

MIT. Upstream copyright: Addy Osmani. See [LICENSE](LICENSE).
