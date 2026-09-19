---
name: ship
description: Codex shortcut for the shipping lifecycle. Use only when the user explicitly invokes $ship.
---

# Ship

Read and follow `../shipping-and-launch/SKILL.md` in full.

Treat `$ship` as an explicit request for a final release decision. When subagents are available and the change is non-trivial, run code review, security audit, and test coverage analysis in parallel, then merge their findings into the canonical launch checklist, go/no-go decision, and rollback plan. For a small low-risk change, perform those checks directly in the current context.
