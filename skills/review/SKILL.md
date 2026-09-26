---
name: review
description: Lifecycle shortcut for reviewing changes before merge. Use only when the user explicitly invokes $review in Codex or /agent-skills:review in Claude Code.
disable-model-invocation: true
---

# Review

Read and follow `../code-review-and-quality/SKILL.md` in full.

Treat `$review` (Codex) or `/agent-skills:review` (Claude Code) as an explicit request to review the current diff or the range named by the user. Report actionable findings first with exact file and line references, then summarize verification and residual risk. Include security, test coverage, and web performance perspectives when they apply. If subagents (Codex subagents or the Claude Code Agent tool) are available and useful, delegate independent read-only passes; otherwise perform those passes in this session. Do not require custom agent configuration.
