---
name: test
description: Run TDD workflow — write failing tests, implement, verify. For bugs, use the Prove-It pattern. Use when the user runs /test in Zed or Delta, or /agent-skills:test in Grok Build.
disable-model-invocation: true
---

Follow the `test-driven-development` skill in this same `.agents/skills/` tree.

## Harness

- **Grok Build:** `/agent-skills:test`.
- **Zed / Zed Delta:** `/test` (this skill).

For new features:

1. Write tests that describe the expected behavior (they should FAIL)
2. Implement the code to make them pass
3. Refactor while keeping tests green

For bug fixes (Prove-It pattern):

1. Write a test that reproduces the bug (must FAIL)
2. Confirm the test fails
3. Implement the fix
4. Confirm the test passes
5. Run the full test suite for regressions

For browser-related issues, also follow `browser-testing-with-devtools` to verify with Chrome DevTools MCP.
