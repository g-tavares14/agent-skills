# Agent Personas

Specialist personas that play a single role with a single perspective. Each persona is a Markdown file under `agents/`. On Grok Build, spawn them with `spawn_subagent` and `subagent_type` matching the persona `name` when that agent is loaded (`code-reviewer`, or `agent-skills:code-reviewer` when this pack is installed as a plugin).

| Persona | Role | Best for |
|---------|------|----------|
| [code-reviewer](../agents/code-reviewer.md) | Senior Staff Engineer | Five-axis review before merge |
| [security-auditor](../agents/security-auditor.md) | Security Engineer | Vulnerability detection, OWASP-style audit |
| [test-engineer](../agents/test-engineer.md) | QA Engineer | Test strategy, coverage analysis, Prove-It pattern |
| [web-performance-auditor](../agents/web-performance-auditor.md) | Web Performance Engineer | Core Web Vitals audit, loading/rendering/network analysis |

## How personas relate to skills and commands

Three layers, each with a distinct job:

| Layer | What it is | Example | Composition role |
|-------|-----------|---------|------------------|
| **Skill** | A workflow with steps and exit criteria | `code-review-and-quality` | The *how* — invoked from inside a persona or command |
| **Persona** | A role with a perspective and an output format | `code-reviewer` | The *who* — adopts a viewpoint, produces a report |
| **Command** | A user-facing entry point | `/agent-skills:review`, `/agent-skills:ship` | The *when* — composes personas and skills |

The user (or a slash command) is the orchestrator. **Personas do not call other personas.** Skills are mandatory hops inside a persona's workflow.

## When to use each

### Direct persona invocation
Pick this when you want one perspective on the current change and the user is in the loop.

- "Review this PR" → invoke `code-reviewer` directly
- "Are there security issues in `auth.ts`?" → invoke `security-auditor` directly
- "What tests are missing for the checkout flow?" → invoke `test-engineer` directly
- "Audit Core Web Vitals on the product page" → invoke `web-performance-auditor` directly

### Slash command (single persona behind it)
Pick this when there's a repeatable workflow you'd otherwise re-explain every time.

- `/agent-skills:review` → wraps `code-reviewer` with the project's review skill
- `/agent-skills:test` → wraps `test-engineer` with TDD skill
- `/agent-skills:webperf` → wraps `web-performance-auditor` for performance-focused audits on web apps

### Slash command (orchestrator — fan-out)
Pick this only when **independent** investigations can run in parallel and produce reports that a single agent then merges.

- `/agent-skills:ship` → fans out to `code-reviewer` + `security-auditor` + `test-engineer` in parallel, then synthesizes their reports into a go/no-go decision

This is the only orchestration pattern this repo endorses. See [references/orchestration-patterns.md](../references/orchestration-patterns.md) for the full pattern catalog and anti-patterns.

## Decision matrix

```
Is the work a single perspective on a single artifact?
├── Yes → Direct persona invocation
└── No  → Are the sub-tasks independent (no shared mutable state, no ordering)?
         ├── Yes → Slash command with parallel fan-out (e.g. /agent-skills:ship)
         └── No  → Sequential slash commands run by the user (/agent-skills:spec → /agent-skills:plan → /agent-skills:build → /agent-skills:test → /agent-skills:review)
```

## Worked example: valid orchestration

`/agent-skills:ship` is the canonical fan-out orchestrator in this repo:

```
/agent-skills:ship
  ├── (parallel) code-reviewer    → review report
  ├── (parallel) security-auditor → audit report
  └── (parallel) test-engineer    → coverage report
                  ↓
        merge phase (main agent)
                  ↓
        go/no-go decision + rollback plan
```

Why this works:
- Each sub-agent operates on the same diff but produces a **different perspective**
- They have no dependencies on each other → genuine parallelism, real wall-clock savings
- Each runs in a fresh context window → main session stays uncluttered
- The merge step is small and benefits from full context, so it stays in the main agent

## Worked example: invalid orchestration (do not build this)

A `meta-orchestrator` persona whose job is "decide which other persona to call":

```
/work-on-pr → meta-orchestrator
                  ↓ (decides "this needs a review")
              code-reviewer
                  ↓ (returns)
              meta-orchestrator (paraphrases result)
                  ↓
              user
```

Why this fails:
- Pure routing layer with no domain value
- Adds two paraphrasing hops → information loss + 2× token cost
- The user already knows they want a review; let them call `/agent-skills:review` directly
- Replicates work that slash commands and `AGENTS.md` intent-mapping already do

## Rules for personas

1. A persona is a single role with a single output format. If you find yourself adding a second role, create a second persona.
2. **Personas do not invoke other personas.** Composition is the job of slash commands or the user. Grok Build also forbids nested `spawn_subagent` (depth is one).
3. A persona may invoke skills (the *how*).
4. Every persona file ends with a "Composition" block stating where it fits.

## Grok Build

Personas in `agents/` load as plugin agent types (`agent-skills:code-reviewer`, …) when this plugin is enabled, and as project agents from `.grok/agents/` when this repo is the cwd. `/agent-skills:ship` is the canonical fan-out: three `spawn_subagent` calls in one turn, then merge in the parent.

Plugin agent frontmatter cannot declare `hooks`, `mcpServers`, or `permissionMode: bypassPermissions` — Grok ignores those fields. Do not rely on them when authoring personas here.

## Zed Agent and Zed Delta

Zed and Delta do not load `agents/*.md` as named agent types. They load skills from `.agents/skills/` (project) and `~/.agents/skills/` (global). This pack keeps that tree **flat** because Zed does not discover nested skill folders. Delta could nest; we still do not, so one tree serves both.

Lifecycle entry points are always `/agent-skills:<name>` (`spec`, `plan`, `build`, `test`, `constraints`, `review`, `code-simplify`, `webperf`, `ship`). Wrappers set `disable-model-invocation: true`. Zed/Delta cannot register `:` in a skill name, so the slash picker aliases are `/spec`, `/plan`, `/build`, `/test`, `/constraints`, `/code-review`, `/code-simplify`, `/webperf`, `/ship`. If the user types `/agent-skills:spec` (etc.) in the composer, run the pack command anyway. **Do not name a skill `review`** — Delta's `/review` is a built-in product command; pack review is `/agent-skills:review`.

When a wrapper needs a persona:

| Product | How to spawn | How to apply the persona |
|---------|--------------|--------------------------|
| Grok Build | `spawn_subagent` | `subagent_type` matching the persona name |
| Zed | `spawn_agent` | Prepend `<pack-root>/agents/<role>.md` |
| Zed Delta | subagent | Reviewer for `code-reviewer`; Worker for `security-auditor` and `test-engineer`; Scout when the work is read-only gather. Prepend the same persona file. |

`/ship` still fans out three specialists in one turn, then merges in the parent. The `simplify-ignore` hook does not run on Zed or Delta.

## Adding a new persona

1. Create `agents/<role>.md` with the same frontmatter format used by existing personas.
2. Define the role, scope, output format, and rules.
3. Add a **Composition** block at the bottom (Invoke directly when / Invoke via / Do not invoke from another persona).
4. Add the persona to the table at the top of this file.
5. If the persona enables a new orchestration pattern, document it in `references/orchestration-patterns.md` rather than inventing the pattern in the persona file itself.
