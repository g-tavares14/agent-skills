---
name: ship
description: Pre-launch checklist via parallel specialist personas, then a go/no-go decision. Use when the user runs /ship in Zed or Delta, or /agent-skills:ship in Grok Build.
disable-model-invocation: true
---

Follow the `shipping-and-launch` skill in this same `.agents/skills/` tree.

`/ship` (Zed / Delta) and `/agent-skills:ship` (Grok) are a **fan-out orchestrator**. Run three specialist personas in parallel against the current change, then merge their reports into a single go/no-go decision with a rollback plan. The personas operate independently — no shared state, no ordering — which is what makes parallel execution safe and useful here.

## Harness

- **Grok Build:** `spawn_subagent` with `code-reviewer`, `security-auditor`, and `test-engineer` (or `agent-skills:<name>` when this pack is the plugin). Fallback: `general-purpose` with the persona file prepended.
- **Zed:** three `spawn_agent` calls; prepend `<pack-root>/agents/<role>.md` to each prompt.
- **Zed Delta:** three subagents — Reviewer for `code-reviewer`, Worker for `security-auditor`, Worker for `test-engineer`. Prepend the same persona files. Delta has no custom agent types from `agents/*.md`.

**Issue all three spawn calls in a single assistant turn** so they run in parallel. Sequential calls defeat the purpose of this command.

## Pack root

Resolve this skill folder (follow symlinks). Pack root is the directory that contains `skills/`, `agents/`, and `.agents/`. Personas:

- `<pack-root>/agents/code-reviewer.md`
- `<pack-root>/agents/security-auditor.md`
- `<pack-root>/agents/test-engineer.md`

## Phase A — Parallel fan-out

Dispatch each persona:

1. **`code-reviewer`** — Run a five-axis review (correctness, readability, architecture, security, performance) on the staged changes or recent commits. Output the standard review template.
2. **`security-auditor`** — Run a vulnerability and threat-model pass. Check OWASP Top 10, secrets handling, auth/authz, dependency CVEs. Output the standard audit report.
3. **`test-engineer`** — Analyze test coverage for the change. Identify gaps in happy path, edge cases, error paths, and concurrency scenarios. Output the standard coverage analysis.

If subagents are unavailable, invoke each persona sequentially in the main context and treat their outputs as if returned in parallel — the merge phase still works.

Constraints:

- Subagents run in isolated context loops and return only their report to this main session.
- Do not let one persona delegate to another — keep the fan-out flat.
- For richer multi-agent collaboration, see `references/orchestration-patterns.md` at the pack root.

## Phase B — Merge in main context

Once all three reports are back, the main agent (not a sub-persona) synthesizes them:

1. **Code Quality** — Aggregate Critical/Important findings from `code-reviewer` and any failing tests, lint, or build output. Resolve duplicates between reviewers.
2. **Security** — Promote any Critical/High `security-auditor` findings to launch blockers. Cross-reference with `code-reviewer`'s security axis.
3. **Performance** — Pull from `code-reviewer`'s performance axis; cross-check Core Web Vitals if applicable.
4. **Accessibility** — Verify keyboard nav, screen reader support, contrast (not covered by the three personas — handle directly here, or invoke the accessibility checklist).
5. **Infrastructure** — Env vars, migrations, monitoring, feature flags. Verify directly.
6. **Documentation** — README, ADRs, changelog. Verify directly.

## Phase C — Decision and rollback

Produce a single output:

```markdown
## Ship Decision: GO | NO-GO

### Blockers (must fix before ship)
- [Source persona: Critical finding + file:line]

### Recommended fixes (should fix before ship)
- [Source persona: Important finding + file:line]

### Acknowledged risks (shipping anyway)
- [Risk + mitigation]

### Rollback plan
- Trigger conditions: [what signals would prompt rollback]
- Rollback procedure: [exact steps]
- Recovery time objective: [target]

### Specialist reports (full)
- [code-reviewer report]
- [security-auditor report]
- [test-engineer report]
```

## Rules

1. The three Phase A personas run in parallel — never sequentially.
2. Personas do not call each other. The main agent merges in Phase B.
3. The rollback plan is mandatory before any GO decision.
4. If any persona returns a Critical finding, the default verdict is NO-GO unless the user explicitly accepts the risk.
5. **Skip the fan-out only if all of the following are true:** the change touches 2 files or fewer, the diff is under 50 lines, and it does not touch auth, payments, data access, or config/env. Otherwise, default to fan-out.
