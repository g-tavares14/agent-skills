# simplify-ignore protected blocks

Mark code that the `code-simplification` skill must preserve. The agent sees the code normally; the hook prevents Claude Code edits from changing marked blocks.

```typescript
/* simplify-ignore-start: perf-critical */
// Keep this manually unrolled implementation for measured performance.
result[0] = buffer[0] ^ key[0];
result[1] = buffer[1] ^ key[1];
/* simplify-ignore-end */
```

The `reason` after `simplify-ignore-start:` is optional. Use matching start and end markers on dedicated lines. Any comment style works. Single-line blocks are supported.

## Hook behavior

`hooks/hooks.json` registers a `PreToolUse` hook for `Edit`, `MultiEdit`, and `Write`. For files that contain protected blocks, it applies the requested replacements or the new content in memory and denies the call when a protected block changes, disappears, has malformed markers, or the edit text is missing or ambiguous. It never writes to source files, creates backups, or uses a workspace cache. Plugin hooks are active once the plugin is enabled; inspect them with `/hooks`.

## Coverage limits

- The hook checks `Edit`, `MultiEdit`, and `Write` calls. It does not inspect shell commands, external editors, formatters, or MCP tools that write files.
- The hook is a guardrail, not a complete security boundary. Keep the `code-simplification` instructions and the `/review` diff check in place.
- Ambiguous edit text fails closed for files that contain protected blocks. Include enough unique context around the intended edit.
- If the plugin is disabled or Python 3 is unavailable, the protection check does not run; preserve marked code by following the skill instructions and review the diff.
