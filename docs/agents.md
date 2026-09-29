# Specialist workflows in Claude Code

`setup-project` installs the `implementer` and `reviewer` agents with the core skills. The review shortcut (`/review` in a set-up project) is the review orchestrator; it uses the current session and can delegate independent, read-only passes to subagents (the Agent tool) when they are available.

| Perspective | Reusable workflow | Supporting reference |
|---|---|---|
| Code quality | `code-review-and-quality` | `catalog/references/definition-of-done.md` |
| Security | `security-and-hardening` | `catalog/references/security-checklist.md` |
| Test coverage | `test-driven-development` | `catalog/references/testing-patterns.md` |
| Web performance | `performance-optimization` | `catalog/references/performance-checklist.md` |

## Review behavior

1. Start with `code-review-and-quality` and report concrete findings with file and line references.
2. Apply the security perspective when authentication, authorization, input validation, data handling, external calls, or dependencies changed.
3. Check tests and coverage for behavior that changed. Do not report tests as passing unless they ran.
4. Apply web performance checks only to browser-facing changes.
5. Use subagents only for independent read-only investigations. If they are unavailable or unnecessary, complete the applicable passes in the main session.
6. Merge findings once, remove duplicates, and state residual risk.

The user remains the orchestrator of the lifecycle. The main sequence is spec → plan → build → verify → review (`/spec` … `/review` in a set-up project); each stage retains its own decision point.
