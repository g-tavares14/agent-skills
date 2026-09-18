# Agent Skills (Grok Build)

Engineering skills, specialist agents, lifecycle slash commands, and the `/agent-skills:code-simplify` hook — packaged for **Grok Build**. Examples are **TypeScript and Python only**.

Derived from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).

```
  DEFINE                 PLAN                  BUILD                 VERIFY                REVIEW                 SHIP
  /agent-skills:spec     /agent-skills:plan    /agent-skills:build   /agent-skills:test    /agent-skills:review   /agent-skills:ship
```

Always invoke this pack as `/agent-skills:<command>`. That is the plugin namespace, so it never steals Grok's `/plan` or `/review`. Grok may still list an uncontested short alias (`/spec`, `/build`, …) in the menu — use the prefixed form anyway.

## Install

From this repo:

```bash
./scripts/install-grok.sh
```

That validates the plugin, installs it with `--trust`, enables `agent-skills`, and merges `plugins.paths` / `plugins.enabled` into `~/.grok/config.toml` so the pack is the default on every project. Re-run after you pull changes.

This repo needs folder trust for `AGENTS.md` and project discovery: `grok --trust` or `/hooks-trust`. Confirm with `grok inspect`.

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

## Layout

| Path | Role |
|------|------|
| `skills/` | 25 workflows |
| `agents/` | 4 personas |
| `commands/*.md` | Grok slash commands |
| `hooks/hooks.json` | Plugin hook (`simplify-ignore`) |
| `references/` | Shared checklists |
| `plugin.json` | Grok plugin manifest |
| `.grok-plugin/marketplace.json` | Marketplace index |
| `.grok/{skills,agents}` | Symlinks for discovery when this repo is cwd |
| `scripts/install-grok.sh` | Apply this pack as the Grok Build default |

## License

MIT. Upstream copyright: Addy Osmani. See `LICENSE`.
