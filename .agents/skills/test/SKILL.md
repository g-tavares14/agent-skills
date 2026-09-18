---
name: test
description: Run TDD workflow — write failing tests, implement, verify. For bugs, use the Prove-It pattern. Use when the user runs /agent-skills:test (any harness). Zed/Delta slash-picker alias: /test.
disable-model-invocation: true
---

Follow the `test-driven-development` skill in this same `.agents/skills/` tree.

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:test`**.

Zed and Delta cannot register `:` in a skill name, so the slash picker alias is `/test`. If the user types `/agent-skills:test` in the composer, run this skill anyway.

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
