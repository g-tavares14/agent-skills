<!-- agent-skills-pack:start -->
# Default pack: agent-skills

This machine's default engineering pack for **Zed Agent** and **Zed Delta** is **agent-skills** (the same pack Grok loads as plugin `agent-skills`).

- Global skills: `~/.agents/skills/` (every project)
- Pack root: `__PACK_ROOT__`
- Personas: `__PACK_ROOT__/agents/<role>.md`

At the start of a task, load `using-agent-skills` and follow the matching workflow. Skills are workflows, not suggestions — do not skip verification.

Canonical lifecycle commands (same string on Grok, Zed, and Delta):
`/agent-skills:spec` `/agent-skills:plan` `/agent-skills:build` `/agent-skills:test` `/agent-skills:constraints` `/agent-skills:review` `/agent-skills:code-simplify` `/agent-skills:webperf` `/agent-skills:ship`

If the user types `/agent-skills:spec` (or any of the above) in Zed or Delta, run that pack command even if the slash picker did not attach a skill. Zed/Delta cannot register `:` in a skill name, so the picker aliases are `/spec` `/plan` `/build` `/test` `/constraints` `/code-review` `/code-simplify` `/webperf` `/ship`.

Use `/agent-skills:review` (picker `/code-review`) for this pack's five-axis review. Delta's `/review` is a different built-in.

Intent → skill:

- New feature → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation` → `test-driven-development`
- Bug → `debugging-and-error-recovery`
- Review → `code-review-and-quality`
- Refactor → `code-simplification`
- API / module boundary → `api-and-interface-design`
- UI → `frontend-ui-engineering`
- Launch → `shipping-and-launch` (`/agent-skills:ship` fans out `code-reviewer`, `security-auditor`, `test-engineer`)

Subagents: Zed uses `spawn_agent` and prepends the persona file. Delta uses Worker / Scout / Reviewer and prepends the same file (Reviewer for `code-reviewer`, Worker for the other two).

Pack examples are TypeScript and Python only.
<!-- agent-skills-pack:end -->
