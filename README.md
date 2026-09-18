# Agent Skills (Grok Build, Zed, Zed Delta)

Engineering skills, specialist agents, and lifecycle slash commands — packaged for **Grok Build**, **Zed Agent**, and **Zed Delta**. Examples are **TypeScript and Python only**.

Derived from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).

```
  DEFINE     PLAN      BUILD      VERIFY     REVIEW          SHIP
  /spec      /plan     /build     /test      /code-review    /ship     Zed / Delta
  /agent-skills:spec   …         …          …   /agent-skills:review   /agent-skills:ship   Grok
```

On **Grok Build**, always invoke this pack as `/agent-skills:<command>`. That is the plugin namespace, so it never steals Grok's `/plan` or `/review`.

On **Zed** and **Zed Delta**, slash names are the skill `name` (hyphens only, no colon). Delta's `/review` is a built-in product command — this pack's review is `/code-review`.

## Install

### Grok Build

```bash
./scripts/install-grok.sh
```

Validates the plugin, installs it with `--trust`, enables `agent-skills`, and merges `plugins.paths` / `plugins.enabled` into `~/.grok/config.toml`. Re-run after you pull changes.

This repo needs folder trust for `AGENTS.md` and project discovery: `grok --trust` or `/hooks-trust`. Confirm with `grok inspect`.

### Zed and Zed Delta

Both load the same Agent Skills roots — there is no separate Delta layout in this pack:

| Scope | Path |
|-------|------|
| Project | `.agents/skills/` in this repo (flat; Zed does not nest) |
| Global | `~/.agents/skills/` (symlink farm from this repo) |

```bash
./scripts/install-zed.sh
```

That links every skill and lifecycle wrapper into `~/.agents/skills/` so they apply in every project, and hides those copies from Grok (`[skills].ignore`) so the Grok plugin stays the source of truth. Re-run after you pull. Uninstall with `./scripts/install-zed.sh --uninstall`.

Grant worktree trust in Zed/Delta so the project copy can load. Delta-only `.delta/skills/` is unused on purpose — one tree serves both products.

The `simplify-ignore` hook is **Grok-only**. Zed and Delta have no equivalent in this pack.

## Commands

| Lifecycle | Grok Build | Zed / Zed Delta | Skill / persona |
|-----------|------------|-----------------|-----------------|
| Spec | `/agent-skills:spec` | `/spec` | `spec-driven-development` |
| Plan | `/agent-skills:plan` | `/plan` | `planning-and-task-breakdown` |
| Build | `/agent-skills:build` | `/build` | `incremental-implementation` + `test-driven-development` |
| Build (all) | `/agent-skills:build auto` | `/build auto` | same |
| Test | `/agent-skills:test` | `/test` | `test-driven-development` |
| Constraints | `/agent-skills:constraints` | `/constraints` | `constraint-driven-development` |
| Review | `/agent-skills:review` | `/code-review` | `code-review-and-quality` |
| Simplify | `/agent-skills:code-simplify` | `/code-simplify` | `code-simplification` |
| Web perf | `/agent-skills:webperf` | `/webperf` | `web-performance-auditor` |
| Ship | `/agent-skills:ship` | `/ship` | `shipping-and-launch` + parallel personas |

Lifecycle wrappers in `.agents/skills/` set `disable-model-invocation: true` so they only run when you type the slash command. The 25 workflow skills stay auto-invocable.

## Layout

| Path | Role |
|------|------|
| `skills/` | 25 workflows (canonical) |
| `agents/` | 4 personas (Grok agent types; Zed/Delta read the files when spawning) |
| `commands/*.md` | Grok slash commands |
| `.agents/skills/` | Zed / Delta: symlinks to `skills/` plus lifecycle wrappers |
| `hooks/hooks.json` | Grok plugin hook (`simplify-ignore`) |
| `references/` | Shared checklists |
| `plugin.json` | Grok plugin manifest |
| `.grok-plugin/marketplace.json` | Marketplace index |
| `.grok/{skills,agents}` | Symlinks for Grok discovery when this repo is cwd |
| `scripts/install-grok.sh` | Apply this pack as the Grok Build default |
| `scripts/install-zed.sh` | Apply this pack as the Zed / Delta default |

## Harness notes

| | Grok Build | Zed Agent | Zed Delta |
|--|------------|-----------|-----------|
| Skills | Plugin `skills/` + `commands/` | `.agents/skills/` (flat) | `.agents/skills/` (nesting allowed, this pack stays flat) |
| Slash | `/agent-skills:<name>` | `/<name>` | `/<name>` |
| Subagents | `spawn_subagent` + `agents/*.md` types | `spawn_agent`; prepend persona files | Worker / Scout / Reviewer; prepend persona files |
| Hooks | `simplify-ignore` | none from this pack | none from this pack |

## License

MIT. Upstream copyright: Addy Osmani. See `LICENSE`.
