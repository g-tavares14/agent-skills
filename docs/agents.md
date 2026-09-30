# Specialist workflows in Claude Code

`setup-project` installs the `implementer` and `reviewer` agents with the core skills. The build shortcut (`/build` in a set-up project) orchestrates them, so the user never has to call them by name. The review shortcut (`/review` in a set-up project) is the review orchestrator; it uses the current session and can delegate independent, read-only passes to subagents (the Agent tool) when they are available.

| Perspective | Reusable workflow | Supporting reference |
|---|---|---|
| Code quality | `code-review-and-quality` | `catalog/references/definition-of-done.md` |
| Security | `security-and-hardening` | `catalog/references/security-checklist.md` |
| Test coverage | `test-driven-development` | `catalog/references/testing-patterns.md` |
| Web performance | `performance-optimization` | `catalog/references/performance-checklist.md` |

## Build behavior

1. The main session reads the next task (or the named one) and hands it to the `implementer`, one task per call.
2. When the implementer delivers, the `reviewer` checks the task's diff without editing it.
3. `blocking` and `important` findings go back to the implementer, for at most two fix rounds; after that, and whenever the implementer stops or disagrees, the user decides.
4. After an approved review the main session marks the task ✅ in `tasks/todo.md`. Checkpoints stay with the user, and `auto` stops at each one.
5. Without the agents (the plugin used before `setup-project`), `/build` implements in the main session with `incremental-implementation` and `test-driven-development`.

## Review behavior

1. Start with `code-review-and-quality` and report concrete findings with file and line references.
2. Apply the security perspective when authentication, authorization, input validation, data handling, external calls, or dependencies changed.
3. Check tests and coverage for behavior that changed. Do not report tests as passing unless they ran.
4. Apply web performance checks only to browser-facing changes.
5. Use subagents only for independent read-only investigations. If they are unavailable or unnecessary, complete the applicable passes in the main session.
6. Merge findings once, remove duplicates, and state residual risk.

The user remains the orchestrator of the lifecycle. The main sequence is spec → plan → build → verify → review (`/spec` … `/review` in a set-up project); each stage retains its own decision point.
