---
name: code-review
description: Five-axis code review — correctness, readability, architecture, security, performance. Use when the user runs /code-review in Zed or Delta, or /agent-skills:review in Grok Build. Not Delta's built-in /review.
disable-model-invocation: true
---

Follow the `code-review-and-quality` skill in this same `.agents/skills/` tree.

## Harness

- **Grok Build:** `/agent-skills:review` (Grok's built-in `/review` is a different command).
- **Zed:** `/code-review` (this skill).
- **Zed Delta:** `/code-review` (this skill). Delta's `/review` is a built-in product command — do not steal it.

Review the current changes (staged or recent commits) across all five axes:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use `security-and-hardening`)
5. **Performance** — No N+1 queries? No unbounded ops? (Use `performance-optimization`)

Categorize findings as Critical, Important, or Suggestion.
Output a structured review with specific file:line references and fix recommendations.
