---
name: code-simplify
description: Simplify code for clarity without changing behavior. Use when the user runs /code-simplify in Zed or Delta, or /agent-skills:code-simplify in Grok Build.
disable-model-invocation: true
---

Follow the `code-simplification` skill in this same `.agents/skills/` tree.

## Harness

- **Grok Build:** `/agent-skills:code-simplify`. The `simplify-ignore` hook is Grok-only.
- **Zed / Zed Delta:** `/code-simplify` (this skill). No equivalent hook — stay inside the requested scope.

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
