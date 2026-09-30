---
name: setup-project
description: Sets up a project with its own copy of the agent-skills workflow (core skills, implementer and reviewer agents, AGENTS.md) or adds catalog skills to it. Use when the user asks to set up a project for agent skills, or approves adding a catalog skill that a spec or plan suggested.
---

# Setup Project

The agent-skills catalog is not loaded globally. Each project gets its own copy of the skills it uses under
`.claude/`, versions it with the code, and adapts it freely. This skill copies from the catalog; it never
decides which skills a project needs. The core is fixed, and the rest is suggested by `spec` and `plan`
from `.claude/catalog.md` and added only with the owner's approval.

All file work is done by `scripts/setup_project.py` in this skill's directory (the base directory shown when
the skill loads). Run it with `python3`, from the project root or with `--project <dir>`.

| Command | Does |
|---|---|
| `install` | Core skills from `catalog/core.txt`, the `implementer` and `reviewer` agents, `AGENTS.md` and `CLAUDE.md` templates, and the index `.claude/catalog.md` |
| `add <skill> ...` | One or more catalog skills, plus the sibling skills and shared references they link to |

Both rewrite `.claude/catalog.md`. The script never overwrites a file that already exists in the project: it reports
it as `kept`. To take a newer catalog version of a skill, diff the project copy against `catalog/skills/<skill>/` in
the plugin and merge by hand, keeping the project's adaptations.

## Install

1. Confirm the project root with the user if the current directory is not obviously it.
2. Run `install` and show the report.
3. If `AGENTS.md` was created from the template, fill it with the user: read the project's manifest files
   (e.g. `package.json`, `pyproject.toml`) for the stack and commands, and ask for what cannot be read.
   The agents rely on the commands section to type-check and test.
4. If the project already had agents with other names, point out the new `implementer.md` and `reviewer.md` and ask
   which to keep; do not delete either.
5. Remind the user to version `.claude/` (skills, agents, references, `catalog.md`) and to keep
   `.claude/settings.local.json` out of git.
6. Suggest writing the first spec with `/spec`: that is where the project-specific skills get chosen.

## Add

Only add skills the user approved. Run `add` with the names, show the report, and mention that preloading a skill in
an agent (`skills:` in its frontmatter) is optional: skills not preloaded are still invoked on demand by their
description.

## Rules

- Do not edit the catalog from a project. A skill that proves useful beyond one project is promoted to the catalog in
  the agent-skills repository by the owner.
- Do not commit or push unless the user asks.
