#!/bin/bash
# Install this repo as the default Grok Build plugin on this machine.
# Idempotent: safe to re-run after pulling changes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GROK_HOME="${GROK_HOME:-$HOME/.grok}"
CONFIG="$GROK_HOME/config.toml"
PLUGIN_NAME="agent-skills"

if ! command -v grok >/dev/null 2>&1; then
  printf 'error: grok is not on PATH. Install Grok Build first.\n' >&2
  exit 1
fi

printf 'Repo:   %s\n' "$ROOT"
printf 'Grok:   %s\n' "$(command -v grok)"

printf '\n==> validate plugin\n'
(cd "$ROOT" && grok plugin validate .)

printf '\n==> install + trust + enable\n'
# Local path installs are a snapshot. Uninstall first so the copy matches this repo.
grok plugin uninstall "$PLUGIN_NAME" --confirm 2>/dev/null || true
grok plugin install "$ROOT" --trust
grok plugin enable "$PLUGIN_NAME"

printf '\n==> merge %s\n' "$CONFIG"
python3 - "$CONFIG" "$ROOT" "$PLUGIN_NAME" <<'PY'
import os, re, sys

config_path, repo, plugin = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.dirname(config_path), exist_ok=True)
text = open(config_path, encoding="utf-8").read() if os.path.exists(config_path) else ""

def quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

block = (
    "\n# %s — managed by scripts/install-grok.sh\n"
    "[plugins]\n"
    "paths = [%s]\n"
    "enabled = [%s]\n"
) % (plugin, quote(repo), quote(plugin))

if "[plugins]" not in text:
    with open(config_path, "a", encoding="utf-8") as f:
        f.write(block if text.endswith("\n") or not text else "\n" + block)
    print("appended [plugins] block")
    sys.exit(0)

# Existing [plugins] section: ensure paths contains repo and enabled contains plugin.
m = re.search(r"(?ms)^\[plugins\]\n(.*?)(?=\n\[|\Z)", text)
if not m:
    print("could not parse [plugins]; leaving file unchanged", file=sys.stderr)
    sys.exit(1)
body = m.group(1)

def upsert_list(body, key, value):
    pat = re.compile(r"^" + re.escape(key) + r"\s*=\s*\[(.*?)\]", re.M | re.S)
    mm = pat.search(body)
    if not mm:
        return key + " = [" + quote(value) + "]\n" + body, True
    inner = mm.group(1)
    items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    if value in items:
        return body, False
    items.append(value)
    rendered = key + " = [" + ", ".join(quote(i) for i in items) + "]"
    return pat.sub(rendered, body, count=1), True

body, changed_paths = upsert_list(body, "paths", repo)
body, changed_enabled = upsert_list(body, "enabled", plugin)
if not (changed_paths or changed_enabled):
    print("already configured")
    sys.exit(0)

start, end = m.span()
# m spans from [plugins] through body; rebuild
new_text = text[: m.start()] + "[plugins]\n" + body
if not new_text.endswith("\n") and end == len(text):
    new_text += "\n"
else:
    new_text += text[m.end():]
with open(config_path, "w", encoding="utf-8") as f:
    f.write(new_text)
print("updated [plugins] paths/enabled")
PY

printf '\n==> inspect\n'
(cd "$ROOT" && grok inspect)

printf '\nDone. In a Grok session, /hooks should list agent-skills (simplify-ignore).\n'
printf 'Invoke pack commands as /agent-skills:<name> (spec, plan, build, test, review, ship, …).\n'
printf 'This repo needs folder trust for AGENTS.md: grok --trust  (or /hooks-trust).\n'
