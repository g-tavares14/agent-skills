# Agent Skills (Grok Build + Codex)

Engineering skills, specialist agents, lifecycle slash commands, and the `/agent-skills:code-simplify` hook — packaged for **Grok Build** and **Codex**. Examples are **TypeScript and Python only**.

Derived from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).

```
  DEFINE                 PLAN                  BUILD                 VERIFY                REVIEW                 SHIP
  /agent-skills:spec     /agent-skills:plan    /agent-skills:build   /agent-skills:test    /agent-skills:review   /agent-skills:ship
  $spec                  $plan-work            $build                $test                 $review-code           $ship
```

On **Grok Build**, always invoke this pack as `/agent-skills:<command>`. That is the plugin namespace, so it never steals Grok's `/plan` or `/review`. Grok may still list an uncontested short alias (`/spec`, `/build`, …) in the menu — use the prefixed form anyway.

On **Codex**, invoke a short lifecycle alias with `$`, such as `$spec`, or invoke a canonical skill such as `$spec-driven-development`. Slash commands in `commands/` are Grok-only.

## Install

Choose the native plugin for **Grok Build** or **Codex**. Like the [upstream quick start](https://github.com/addyosmani/agent-skills#quick-start), this pack also supports a skills-only installation with the [skills CLI](https://github.com/vercel-labs/skills).

### Quick start — Grok Build

Run in your terminal with Grok Build and Git installed:

```bash
grok plugin install https://github.com/g-tavares14/grok-agent-skills.git
grok plugin enable agent-skills
grok plugin details agent-skills
```

Review the plugin trust prompt during installation. In Grok, use `/agent-skills:spec`, `/agent-skills:plan`, or `/agent-skills:build`. Review hook trust with `/hooks`.

### Quick start — Codex

Run in your terminal with Git and a Codex CLI that supports `codex plugin`:

```bash
codex plugin marketplace add https://github.com/g-tavares14/grok-agent-skills.git
codex plugin add agent-skills@gtavares-skills
codex plugin list --marketplace gtavares-skills
```

Start a new Codex task and invoke `$spec`. Codex reads the root `skills/` directory through `.codex-plugin/plugin.json`, following the same native packaging model as the upstream repository.

### Optional — only skills in Codex

Requires Node.js/npm (including `npx`) and Git. Run from the project where you want the skills:

```bash
npx skills add g-tavares14/grok-agent-skills --list
npx skills add g-tavares14/grok-agent-skills --agent codex
```

Select the skills interactively, or install a specific one:

```bash
npx skills add g-tavares14/grok-agent-skills --agent codex --skill code-review-and-quality
```

Add `--global` to install for all your projects. This route installs skill folders only and does not include the repo-level `references/` directory used by supplementary checklists. Grok installation uses its native plugin command above.

The short lifecycle aliases delegate to canonical skills. When using the skills-only route, install the complete pack or select each alias together with the canonical workflow listed below.

## Commands

| Command | Skill / persona |
|---------|-----------------|
| `/agent-skills:spec` | `spec-driven-development` |
| `/agent-skills:plan` | `planning-and-task-breakdown` |
| `/agent-skills:build` | `incremental-implementation` + `test-driven-development` |
| `/agent-skills:build auto` | whole plan, one approval |
| `/agent-skills:test` | `test-driven-development` |
| `/agent-skills:constraints` | `constraint-driven-development` |
| `/agent-skills:review` | `code-review-and-quality` |
| `/agent-skills:code-simplify` | `code-simplification` + `simplify-ignore` hook |
| `/agent-skills:webperf` | `web-performance-auditor` |
| `/agent-skills:ship` | `shipping-and-launch` + parallel `code-reviewer`, `security-auditor`, `test-engineer` |

On Codex, use the short lifecycle aliases shown below. Their implicit invocation is disabled, so they do not compete with the canonical skills during automatic skill selection.

| Stage | Codex alias | Canonical workflow |
|-------|-------------|--------------------|
| Define | `$spec` | `$spec-driven-development` |
| Plan | `$plan-work` | `$planning-and-task-breakdown` |
| Build | `$build` | `$incremental-implementation` + `$test-driven-development` |
| Verify | `$test` | `$test-driven-development` |
| Review | `$review-code` | `$code-review-and-quality` |
| Ship | `$ship` | `$shipping-and-launch` |

The full Codex flow is `$spec` → `$plan-work` → `$build` → `$test` → `$review-code` → `$ship`. Use `$build auto` after approving a spec and plan to execute all remaining tasks without pausing between reversible slices.

## Layout

| Path | Role |
|------|------|
| `skills/` | 25 workflows + 6 explicit Codex aliases |
| `agents/` | 4 Grok specialist personas |
| `commands/*.md` | Grok slash commands |
| `hooks/hooks.json` | Grok plugin hook (`simplify-ignore`) |
| `references/` | Shared checklists |
| `plugin.json` | Grok plugin manifest |
| `.grok-plugin/marketplace.json` | Grok marketplace index |
| `.codex-plugin/plugin.json` | Codex plugin manifest |
| `.agents/plugins/marketplace.json` | Codex marketplace catalog |

## License

MIT. Upstream copyright: Addy Osmani. See `LICENSE`.
