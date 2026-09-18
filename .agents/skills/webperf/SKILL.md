---
name: webperf
description: Run a web performance audit via the web-performance-auditor persona. Use when the user runs /agent-skills:webperf (any harness). Zed/Delta slash-picker alias: /webperf.
disable-model-invocation: true
---

Follow `performance-optimization` in this same `.agents/skills/` tree. Load the `web-performance-auditor` persona from the pack (see Pack root).

## Invoke

Canonical command (Grok, Zed, Delta): **`/agent-skills:webperf`**.

Zed and Delta cannot register `:` in a skill name, so the slash picker alias is `/webperf`. If the user types `/agent-skills:webperf` in the composer, run this skill anyway.

## Harness

- **Grok Build:** Spawn `web-performance-auditor` (or `agent-skills:web-performance-auditor`) with `spawn_subagent`.
- **Zed:** Spawn with `spawn_agent` and prepend `<pack-root>/agents/web-performance-auditor.md`.
- **Zed Delta:** Spawn a Scout (read-only gather) or Worker; prepend the same persona file. Delta has no custom agent types.

## Pack root

Resolve this skill folder (follow symlinks). Pack root is the directory that contains `skills/`, `agents/`, and `.agents/`. Persona file: `<pack-root>/agents/web-performance-auditor.md`.

This command targets web applications specifically. Do not use it for utility libraries, CLIs, or server-only code with no browser-facing output.

## Determine the mode

Deep mode — activate when any of these is available:

- A Lighthouse JSON report file (e.g. `npx lighthouse <url> --output json --output-path ./report.json`, or `npx -p chrome-devtools-mcp chrome-devtools lighthouse_audit --output-format=json` from the Chrome DevTools MCP CLI)
- A PageSpeed Insights JSON response (includes Lighthouse + CrUX)
- A CrUX API response (requires $CRUX_API_KEY or $GOOGLE_API_KEY environment variables — never hard-code these values in config files)
- A DevTools performance trace
- A live URL plus the chrome-devtools MCP server configured in the harness (capture metrics directly via lighthouse_audit and performance_* tools)
- The Chrome DevTools MCP CLI invoked locally (via `npx -p chrome-devtools-mcp chrome-devtools <tool>`), passing the JSON output to the agent

Quick mode — default when none of the above are available. Scan source code for structural anti-patterns and label every finding as `potential impact`.

## Run the audit

Spawn one subagent with the persona above. If subagents are unavailable, adopt the persona in the main thread. Pass it explicitly:

- The files, components, or diff under review
- Any artifact paths (Lighthouse JSON, PSI JSON, CrUX response, trace) or pasted JSON content
- The target URL or page name when known
- A note on which mode you expect (Quick or Deep), so the agent surfaces missing inputs if Deep was intended

The subagent returns a scorecard (only populated with sourced values — mark unmeasured fields `not measured`, never fabricate metrics), a ranked list of findings, positive observations, and proactive recommendations.

## Output

Return the full audit report to the user. No synthesis or merge step is needed — this is a single-persona command.
