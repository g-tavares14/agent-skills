# AGENTS.md

Instructions for AI agents working in this repository (Claude Code loads it through `CLAUDE.md`).

## Project

<!-- What this project is, who it is for, and the current stage. -->

## Stack

<!-- Language, runtime, framework, database, test runner. -->

## Commands

<!-- The exact commands to install, run, type-check, lint, and test. The implementer and reviewer agents run these. -->

```bash
# install:
# dev server:
# typecheck:
# test:
```

## Conventions

<!-- Code style, error format, file layout, naming. -->

## Decisions

<!-- Decisions already made and why, so agents don't reopen them. -->

## Security rules

<!-- Rules every change must respect (secrets, auth, data isolation, logging). -->

## Agent workflow

- Lifecycle: `/spec` → `/plan` → `/build` → `/verify` → `/review`. Specs live in the repo; the plan in `tasks/plan.md`, tasks in `tasks/todo.md`.
- Agents: `implementer` implements one task and stops for review; `reviewer` reviews the diff without editing.
- Skills live in `.claude/skills/` and belong to this project: adapt them freely. `.claude/catalog.md` lists catalog skills not installed yet.
- Do not commit or push without the owner asking.
