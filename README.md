# Agent Skills for Claude Code

Engineering workflows and reusable skills for **Claude Code** (CLI, desktop, web, and IDE extensions). The main workflow has five steps: **spec → plan → build → verify → review**. Code examples use TypeScript and Python.

The skills are a **catalog**, not a global install. The plugin loads a single skill, `setup-project`, which copies the skills a project uses into that project's `.claude/` directory. Each project versions its copy with the code and adapts it freely.

## Install

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

The bundled hook (Python 3) checks `Edit`, `MultiEdit`, and `Write` calls for changes to protected blocks (see [hooks/SIMPLIFY-IGNORE.md](hooks/SIMPLIFY-IGNORE.md)).

## Set up a project

In the project root, run `/agent-skills:setup-project`. It installs, without overwriting existing files:

- the **core** skills from `catalog/core.txt`: the lifecycle shortcuts and the skills they and the agents use;
- the `implementer` and `reviewer` agents in `.claude/agents/`;
- `AGENTS.md` and `CLAUDE.md` templates, if the project has none;
- `.claude/catalog.md`, an index of the catalog skills **not** installed, and `.claude/agent-skills.json`, the catalog commit each skill was copied from.

Inside the project the shortcuts are plain project skills: `/spec`, `/plan`, `/build`, `/verify`, `/review`. They only run when you invoke them; the other skills are also picked up automatically when a task matches their description.

Project-specific skills are chosen later: `spec` and `plan` compare the work with `.claude/catalog.md` and suggest skills; the approved ones are added with `/agent-skills:setup-project add <skill>`. Skills that only make sense for one project are written directly in its `.claude/skills/`.

Someone who clones a set-up project needs nothing installed: the skills are in the repository. Only `add` needs the plugin.

## Five-step workflow

| Stage | Shortcut | Canonical workflow |
|---|---|---|
| Specify | `/spec` | `spec-driven-development` |
| Plan | `/plan` | `planning-and-task-breakdown` |
| Build | `/build` | `incremental-implementation` + `test-driven-development` |
| Verify | `/verify` | Acceptance criteria and repository checks |
| Review | `/review` | `code-review-and-quality` plus applicable security, test, and performance checks |

The complete cycle is spec → plan → build → verify → review. Invoke other specialized skills by their names when the task calls for them.

## Layout

| Path | Purpose |
|---|---|
| `skills/setup-project/` | The only globally loaded skill: installs catalog skills into a project |
| `catalog/<category>/` | Skills by specialty: `workflow`, `code-quality`, `backend`, `frontend`, `security`, `performance`, `devops`, `discovery`, `docs-and-context` |
| `catalog/core.txt` | Skills every project gets |
| `catalog/agents/` | `implementer` and `reviewer` agent templates |
| `catalog/templates/` | `AGENTS.md` and `CLAUDE.md` templates |
| `catalog/references/` | Reusable checklists and guidance |
| `hooks/hooks.json` | `PreToolUse` hook for protected code blocks |
| `hooks/simplify_ignore_guard.py` | Read-only edit guard; does not rewrite source files |
| `docs/` | Workflow and specialist guidance |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace |

## Validate local changes

```bash
python3 -m json.tool .claude-plugin/plugin.json
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool hooks/hooks.json
python3 -m unittest discover -s hooks -p 'test_*.py'
python3 -m unittest discover -s skills/setup-project/scripts -p 'test_*.py'
```

MIT. Upstream copyright: Addy Osmani. See [LICENSE](LICENSE).
