---
name: code-review
description: Five-axis code review — correctness, readability, architecture, security, performance. Use when the user runs /agent-skills:review (any harness). Zed/Delta slash-picker alias: /code-review. Not Delta's built-in /review.
disable-model-invocation: true
---

Follow the `code-review-and-quality` skill in this same `.agents/skills/` tree.

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:review`**.

Zed and Delta cannot register `:` in a skill name, and Delta's `/review` is a built-in product command, so the slash picker alias is `/code-review`. If the user types `/agent-skills:review` in the composer, run this skill anyway. Do not treat Delta's `/review` as this pack.

Review the current changes (staged or recent commits) across all five axes:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use `security-and-hardening`)
5. **Performance** — No N+1 queries? No unbounded ops? (Use `performance-optimization`)

Categorize findings as Critical, Important, or Suggestion.
Output a structured review with specific file:line references and fix recommendations.
