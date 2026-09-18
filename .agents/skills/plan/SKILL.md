---
name: plan
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering. Use when the user runs /agent-skills:plan (any harness). Zed/Delta slash-picker alias: /plan.
disable-model-invocation: true
---

Follow the `planning-and-task-breakdown` skill in this same `.agents/skills/` tree.

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:plan`**.

Zed and Delta cannot register `:` in a skill name, so the slash picker alias is `/plan`. If the user types `/agent-skills:plan` in the composer, run this skill anyway. Grok's built-in `/plan` is a different command.

Read the existing spec (SPEC.md or equivalent) and the relevant codebase sections. Then:

1. Enter plan mode — read only, no code changes
2. Identify the dependency graph between components
3. Slice work vertically (one complete path per task, not horizontal layers)
4. Write tasks with acceptance criteria and verification steps
5. Add checkpoints between phases
6. Present the plan for human review

Save the plan to tasks/plan.md and task list to tasks/todo.md.

If tasks/plan.md or tasks/todo.md already exists with unchecked tasks for different work, stop and ask before writing — never silently overwrite an incomplete plan.
