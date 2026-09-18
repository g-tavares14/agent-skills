---
name: code-simplify
description: Simplify code for clarity without changing behavior. Use when the user runs /agent-skills:code-simplify (any harness). Zed/Delta slash-picker alias: /code-simplify.
disable-model-invocation: true
---

Follow the `code-simplification` skill in this same `.agents/skills/` tree.

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:code-simplify`**.

Zed and Delta cannot register `:` in a skill name, so the slash picker alias is `/code-simplify`. If the user types `/agent-skills:code-simplify` in the composer, run this skill anyway. The `simplify-ignore` hook is Grok-only — on Zed/Delta stay inside the requested scope.

Simplify recently changed code (or the specified scope) while preserving exact behavior:

1. Read AGENTS.md and study project conventions
2. Identify the target code — recent changes unless a broader scope is specified
3. Understand the code's purpose, callers, edge cases, and test coverage before touching it
4. Scan for simplification opportunities:
   - Deep nesting → guard clauses or extracted helpers
   - Long functions → split by responsibility
   - Nested ternaries → if/else or switch
   - Generic names → descriptive names
   - Duplicated logic → shared functions
   - Dead code → remove after confirming
5. Apply each simplification incrementally — run tests after each change
6. Verify all tests pass, the build succeeds, and the diff is clean

If tests fail after a simplification, revert that change and reconsider. Use `code-review-and-quality` to review the result.
