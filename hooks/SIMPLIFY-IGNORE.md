# simplify-ignore protected blocks

Mark code that the `code-simplification` skill must preserve. Codex sees the code normally; the hook prevents supported patch operations from changing marked blocks.

```typescript
/* simplify-ignore-start: perf-critical */
// Keep this manually unrolled implementation for measured performance.
result[0] = buffer[0] ^ key[0];
result[1] = buffer[1] ^ key[1];
/* simplify-ignore-end */
```

The `reason` after `simplify-ignore-start:` is optional. Use matching start and end markers on dedicated lines. Any comment style works. Single-line blocks are supported.

## Codex hook behavior

The plugin registers a `PreToolUse` hook for `apply_patch`. It reads the hook event, applies supported patch hunks in memory, and compares marked blocks before and after. It denies a patch if a protected block changes, disappears, has malformed markers, or cannot be analyzed safely. It never writes to source files, creates backups, or uses a workspace cache.

Review and trust the hook definition in Codex before relying on it. In Codex CLI, use `/hooks`. A changed hook definition requires a new trust review.

## Coverage limits

- The hook checks Codex `apply_patch` calls. It does not inspect shell commands, external editors, formatters, or MCP tools that write files.
- The hook is a guardrail, not a complete security boundary. Keep the `code-simplification` instructions and `$review` diff check in place.
- Ambiguous patch context fails closed for files that contain protected blocks. Rework the patch to include unique unchanged context around the intended edit.
- If the hook is not trusted or Python 3 is unavailable, Codex skips the protection check; preserve marked code by following the skill instructions and review the diff.
