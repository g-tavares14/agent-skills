# Agent Skills for Claude Code

**Engineering workflows for Claude Code, copied into each project that uses them.**

Skills encode the workflows, quality gates, and habits senior engineers follow, so the agent applies them the same way every time. This package is a per-project catalog: the plugin loads one skill, `setup-project`, which copies the skills a project needs into its `.claude/` directory. The project versions its copy with the code and adapts it freely. Code examples use TypeScript and Python.

```
  DEFINE          PLAN           BUILD          VERIFY         REVIEW
 ┌──────┐      ┌──────┐      ┌───────────┐   ┌──────┐      ┌──────┐
 │ Spec │ ───▶ │ Task │ ───▶ │implementer│──▶│ Test │ ───▶ │  QA  │
 │      │      │ list │      │ ⇄ reviewer│   │      │      │ Gate │
 └──────┘      └──────┘      └───────────┘   └──────┘      └──────┘
  /spec          /plan          /build         /verify       /review
```

---

## Commands

| What you're doing | Command | Key principle |
|---|---|---|
| Set up a project | `/agent-skills:setup-project` | Copy only what the project uses |
| Define what to build | `/spec` | Spec before code |
| Plan how to build it | `/plan` | Small, verifiable tasks |
| Build it | `/build` | One reviewed task at a time |
| Prove it works | `/verify` | Tests are proof |
| Review before merge | `/review` | Improve code health |

`setup-project` is the only plugin command, so it keeps the plugin prefix. The lifecycle commands are project skills once a project is set up. They run only when you invoke them; the other skills also activate on their own when a task matches their description.

`/build` hands each task to the `implementer` agent, has the `reviewer` agent check the diff, sends findings back for up to two fix rounds, and marks the task done after an approved review. Commits, dependency changes, and migrations stay with you: the agents cannot run them, and the session runs them when you authorize it. **`/build auto`** runs the remaining tasks the same way and stops at every checkpoint in the plan.

---

## Quick Start

Install the plugin inside a Claude Code session:

```text
/plugin marketplace add g-tavares14/agent-skills
/plugin install agent-skills@gtavares-skills
```

Or from a terminal:

```bash
claude plugin marketplace add g-tavares14/agent-skills
```

```bash
claude plugin install agent-skills@gtavares-skills
```

Then, in the root of each project, run `/agent-skills:setup-project`. Without overwriting existing files, it copies:

- the **core** skills listed in `catalog/core.txt` (marked ● below);
- the `implementer` and `reviewer` agents into `.claude/agents/`;
- `AGENTS.md` and `CLAUDE.md` templates, if the project has none;
- `.claude/catalog.md`, the list of catalog skills **not** installed.

The other skills are added when the work calls for them: `/spec` and `/plan` check `.claude/catalog.md` and suggest skills, and the approved ones are added with `/agent-skills:setup-project add <skill>`. Someone who clones a set-up project needs nothing installed; only `add` needs the plugin.

To try a local checkout without installing, start Claude Code with `claude --plugin-dir /path/to/agent-skills`.

---

## All Skills

25 skills plus the five lifecycle commands, all in [catalog/skills/](catalog/skills). ● marks the core skills every project gets.

### Meta: find the right skill

| Skill | Use when |
|---|---|
| [using-agent-skills](catalog/skills/using-agent-skills/SKILL.md) | Starting a session or deciding which skill applies |

### Define: clarify what to build

| Skill | Use when |
|---|---|
| [interview-me](catalog/skills/interview-me/SKILL.md) | The request is underspecified; asks one question at a time |
| [idea-refine](catalog/skills/idea-refine/SKILL.md) | A rough idea needs options and a sharper proposal |
| ● [spec-driven-development](catalog/skills/spec-driven-development/SKILL.md) | Starting a project or significant change without a spec |
| [constraint-driven-development](catalog/skills/constraint-driven-development/SKILL.md) | Defining a measurable quality bar, or a change might weaken it |

### Plan: break it down

| Skill | Use when |
|---|---|
| ● [planning-and-task-breakdown](catalog/skills/planning-and-task-breakdown/SKILL.md) | A spec needs ordered, verifiable tasks |

### Build: write the code

| Skill | Use when |
|---|---|
| ● [incremental-implementation](catalog/skills/incremental-implementation/SKILL.md) | A change touches more than one file or comes from the plan |
| ● [test-driven-development](catalog/skills/test-driven-development/SKILL.md) | Implementing logic, fixing bugs, or changing behavior |
| [context-engineering](catalog/skills/context-engineering/SKILL.md) | Starting a session, switching tasks, or output quality drops |
| [source-driven-development](catalog/skills/source-driven-development/SKILL.md) | Framework or library code must follow the official docs |
| [doubt-driven-development](catalog/skills/doubt-driven-development/SKILL.md) | A high-stakes decision needs an adversarial second look |
| [frontend-ui-engineering](catalog/skills/frontend-ui-engineering/SKILL.md) | Building or changing user-facing interfaces |
| [api-and-interface-design](catalog/skills/api-and-interface-design/SKILL.md) | Designing APIs, module boundaries, or public interfaces |

### Verify: prove it works

| Skill | Use when |
|---|---|
| [browser-testing-with-devtools](catalog/skills/browser-testing-with-devtools/SKILL.md) | Building or debugging anything that runs in a browser |
| [debugging-and-error-recovery](catalog/skills/debugging-and-error-recovery/SKILL.md) | Tests fail, builds break, or behavior is unexpected |

### Review: quality gates before merge

| Skill | Use when |
|---|---|
| ● [code-review-and-quality](catalog/skills/code-review-and-quality/SKILL.md) | Before merging any change |
| ● [code-simplification](catalog/skills/code-simplification/SKILL.md) | Working code is harder to read or maintain than it should be |
| ● [security-and-hardening](catalog/skills/security-and-hardening/SKILL.md) | Handling user input, auth, data storage, or external integrations |
| [performance-optimization](catalog/skills/performance-optimization/SKILL.md) | Performance requirements exist or a regression is suspected |

### Ship: deploy with confidence

| Skill | Use when |
|---|---|
| [git-workflow-and-versioning](catalog/skills/git-workflow-and-versioning/SKILL.md) | Committing, branching, or splitting work |
| [ci-cd-and-automation](catalog/skills/ci-cd-and-automation/SKILL.md) | Setting up or changing build and deploy pipelines |
| [deprecation-and-migration](catalog/skills/deprecation-and-migration/SKILL.md) | Removing old systems or moving users to a new one |
| [documentation-and-adrs](catalog/skills/documentation-and-adrs/SKILL.md) | Recording a decision, changing an API, or shipping a feature |
| [observability-and-instrumentation](catalog/skills/observability-and-instrumentation/SKILL.md) | Adding logs, metrics, tracing, or alerts |
| [shipping-and-launch](catalog/skills/shipping-and-launch/SKILL.md) | Preparing a production deploy, rollout, or rollback plan |

The lifecycle commands ([spec](catalog/skills/spec/SKILL.md), [plan](catalog/skills/plan/SKILL.md), [build](catalog/skills/build/SKILL.md), [verify](catalog/skills/verify/SKILL.md), [review](catalog/skills/review/SKILL.md)) are core too. Each one delegates to the skills above.

---

## Agents

Copied into every project by `setup-project` and orchestrated by `/build`:

| Agent | Role | Limits |
|---|---|---|
| [implementer](catalog/agents/implementer.md) | Implements one planned task with TDD, simplifies its own diff, verifies it for real, and reports | No commits, dependency changes, or migrations |
| [reviewer](catalog/agents/reviewer.md) | Reviews the task's diff against the spec for correctness, tests, security, and quality | Read-only |

See [docs/agents.md](docs/agents.md) for how `/build` and `/review` use them.

---

## Reference Checklists

Shared material that skills cite; `setup-project` copies each one along with the skills that cite it.

| Reference | Covers |
|---|---|
| [definition-of-done.md](catalog/references/definition-of-done.md) | The standing bar every change clears |
| [testing-patterns.md](catalog/references/testing-patterns.md) | Test structure, naming, mocking, and anti-patterns |
| [security-checklist.md](catalog/references/security-checklist.md) | Auth, input validation, headers, and OWASP Top 10 |
| [performance-checklist.md](catalog/references/performance-checklist.md) | Core Web Vitals targets and frontend/backend checks |
| [accessibility-checklist.md](catalog/references/accessibility-checklist.md) | Keyboard, screen readers, ARIA, and testing tools |
| [observability-checklist.md](catalog/references/observability-checklist.md) | Logging, metrics, tracing, and alerting |
| [orchestration-patterns.md](catalog/references/orchestration-patterns.md) | When to use skills versus subagents |

---

## Hooks

The plugin bundles three hooks (Python 3). None of them writes to your project.

- **Session start:** in a git repository without the `implementer` and `reviewer` agents, suggests `/agent-skills:setup-project`.
- **Agent Bash guard:** blocks the `implementer` from committing, changing history, adding or removing dependencies, and applying migrations; blocks the `reviewer` from all of that and from writing files or changing the repository. The main session is never checked. Commands the guard cannot parse are denied. It is a guardrail, not a security boundary: it cannot see what a script or an `npm run` target does.
- **Protected blocks:** stops `Edit`, `MultiEdit`, and `Write` calls from changing `simplify-ignore` blocks (see [hooks/SIMPLIFY-IGNORE.md](hooks/SIMPLIFY-IGNORE.md)).

---

## How Skills Work

Every skill follows the same anatomy:

```
SKILL.md
├── Frontmatter      name, and a description that says when to use it
├── Overview         what the skill does
├── When to Use      triggering conditions
├── Process          step-by-step workflow
├── Rationalizations excuses to skip steps, with rebuttals
├── Red Flags        signs something is wrong
└── Verification     evidence required before calling it done
```

- **Process, not prose.** Skills are workflows with steps, checkpoints, and exit criteria.
- **Verification is required.** Every skill ends with evidence: passing tests, build output, runtime data.
- **Progressive disclosure.** `SKILL.md` is the entry point; references load only when needed.

---

## Project Structure

| Path | Purpose |
|---|---|
| `skills/setup-project/` | The only skill the plugin loads; its script copies catalog files into a project |
| `catalog/skills/` | The 25 skills and the five lifecycle commands |
| `catalog/core.txt` | Skills every project gets |
| `catalog/agents/` | `implementer` and `reviewer` |
| `catalog/references/` | Shared checklists |
| `catalog/templates/` | `AGENTS.md` and `CLAUDE.md` for projects that have none |
| `hooks/` | Hook registration, scripts, and their tests |
| `docs/` | Workflow and agent guidance |
| `.claude-plugin/` | Plugin manifest and marketplace |

Validate local changes with:

```bash
python3 -m json.tool .claude-plugin/plugin.json
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool hooks/hooks.json
python3 -m unittest discover -s hooks -p 'test_*.py'
python3 -m unittest discover -s skills/setup-project/scripts -p 'test_*.py'
```

---

## Credits

Based on [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills). MIT; upstream copyright Addy Osmani. See [LICENSE](LICENSE).
