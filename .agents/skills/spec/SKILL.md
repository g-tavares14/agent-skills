---
name: spec
description: Start spec-driven development — write a structured specification before writing code. Use when the user runs /agent-skills:spec (any harness). Zed/Delta slash-picker alias: /spec.
disable-model-invocation: true
---

Follow the `spec-driven-development` skill in this same `.agents/skills/` tree.

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:spec`**.

Zed and Delta cannot register `:` in a skill name, so the slash picker alias is `/spec`. If the user types `/agent-skills:spec` in the composer, run this skill anyway.

Begin by understanding what the user wants to build. Ask clarifying questions about:

1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

Then generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.

If the request bundles several independently testable capabilities, first propose a capability map (module ids, dependency direction, build order) per the skill's Phase 0 and get it approved, then spec each module in dependency order.

Save the spec as SPEC.md in the project root and confirm with the user before proceeding.
