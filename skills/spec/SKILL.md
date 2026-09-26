---
name: spec
description: Lifecycle shortcut for the specification lifecycle. Use only when the user explicitly invokes $spec in Codex or /agent-skills:spec in Claude Code.
disable-model-invocation: true
---

# Spec

Read and follow `../spec-driven-development/SKILL.md` in full.

Treat `$spec` (Codex) or `/agent-skills:spec` (Claude Code) as an explicit request to start that workflow. Produce or update the project specification, then stop at any approval checkpoint required by the canonical skill.
