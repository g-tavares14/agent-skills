# Orchestration patterns

Use skills to describe repeatable workflows and subagents (Codex subagents or the Claude Code Agent tool) to isolate independent investigations. The user-facing lifecycle remains explicit: `$spec` → `$plan` → `$build` → `$verify` → `$review` in Codex, or `/agent-skills:spec` → `/agent-skills:plan` → `/agent-skills:build` → `/agent-skills:verify` → `/agent-skills:review` in Claude Code.

## Direct work

Use one session when the task has one goal, depends on shared mutable state, or benefits from continuous context. This is the default for implementation and for small reviews.

## Parallel review

For a non-trivial review, independent read-only passes can examine code quality, security, and test coverage concurrently. The main session remains responsible for resolving overlap and producing one report. Add a web performance pass only when the change affects a browser-facing application.

Before delegating, check that each pass has a distinct question, can run without another pass's findings, and can return evidence with file and line references. Do not delegate when setup cost exceeds the value of isolated context.

If subagents are unavailable, perform each applicable pass sequentially in the current session. Never claim a delegated check ran if no subagent was started.

## Avoid unnecessary orchestration

- Do not create a router whose only job is choosing another skill.
- Do not have one specialist recursively invoke another specialist.
- Do not combine dependent lifecycle stages into an automatic chain that skips their review points.
- Keep synthesis in the main session so the user receives one result with traceable evidence.
