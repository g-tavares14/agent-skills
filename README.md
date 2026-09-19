# Agent Skills (Grok Build + Codex)

Engineering skills, specialist agents, lifecycle slash commands, and the `/agent-skills:code-simplify` hook — packaged for **Grok Build** and **Codex**. Examples are **TypeScript and Python only**.

Derived from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).

```
  DEFINE                 PLAN                  BUILD                 VERIFY                REVIEW                 SHIP
  /agent-skills:spec     /agent-skills:plan    /agent-skills:build   /agent-skills:test    /agent-skills:review   /agent-skills:ship
```

On **Grok Build**, always invoke this pack as `/agent-skills:<command>`. That is the plugin namespace, so it never steals Grok's `/plan` or `/review`. Grok may still list an uncontested short alias (`/spec`, `/build`, …) in the menu — use the prefixed form anyway.

On **Codex**, invoke the skill name in chat, for example `@spec-driven-development`. Slash commands in `commands/` are Grok-only.

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

Start a new Codex task and invoke `@spec-driven-development`. Codex reads the root `skills/` directory through `.codex-plugin/plugin.json`, following the same native packaging model as the upstream repository.

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

On Codex, invoke the skill in the right-hand column with `@`, such as `@spec-driven-development`, instead of the Grok slash command.

## Layout

| Path | Role |
|------|------|
| `skills/` | 25 workflows |
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
