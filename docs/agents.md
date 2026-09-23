# Specialist workflows in Codex

The plugin distributes skills and reference material. It does not require a separate custom-agent installation. The `$review` shortcut is the review orchestrator; it uses the current Codex session and can delegate independent, read-only passes to Codex subagents when they are available.

| Perspective | Reusable workflow | Supporting reference |
|---|---|---|
| Code quality | `code-review-and-quality` | `references/definition-of-done.md` |
| Security | `security-and-hardening` | `references/security-checklist.md` |
| Test coverage | `test-driven-development` | `references/testing-patterns.md` |
| Web performance | `performance-optimization` | `references/performance-checklist.md` |

## Review behavior

1. Start with `code-review-and-quality` and report concrete findings with file and line references.
2. Apply the security perspective when authentication, authorization, input validation, data handling, external calls, or dependencies changed.
3. Check tests and coverage for behavior that changed. Do not report tests as passing unless they ran.
4. Apply web performance checks only to browser-facing changes.
5. Use subagents only for independent read-only investigations. If subagents are unavailable or unnecessary, complete the applicable passes in the main session.
6. Merge findings once, remove duplicates, and state residual risk.

The user remains the orchestrator of the lifecycle. The main sequence is `$spec` → `$plan` → `$build` → `$verify` → `$review`; each stage retains its own decision point.
