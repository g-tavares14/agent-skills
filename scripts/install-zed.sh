#!/bin/bash
# Install this pack as the machine default for Zed Agent and Zed Delta.
#
# Skills (every project):
#   ~/.agents/skills/              global
#   <worktree>/.agents/skills/     already in this repo (flat — Zed cannot nest)
#
# Always-on instructions (Grok analog of enabling the plugin in config.toml):
#   Zed:   AGENTS.md next to settings.json (~/.config/zed/AGENTS.md)
#   Delta: ~/.config/delta/AGENTS.md, plus the folder that holds settings.json
#
# Delta-only .delta/skills/ is not used. Review in this pack is /code-review
# because Delta's /review is a built-in product command.
#
# Grok Build also scans .agents/skills (project and ~/.agents/skills). This
# script hides those copies from Grok via [skills].ignore so the plugin stays
# the Grok source of truth.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_HOME="${AGENTS_HOME:-$HOME/.agents}"
DEST="$AGENTS_HOME/skills"
SRC="$ROOT/.agents/skills"
GROK_HOME="${GROK_HOME:-$HOME/.grok}"
GROK_CONFIG="$GROK_HOME/config.toml"
MARKER="$AGENTS_HOME/.agent-skills-pack-root"
MERGE="$ROOT/scripts/merge-grok-skills-ignore.py"
MERGE_AGENTS="$ROOT/scripts/merge-agents-md.py"
TEMPLATE="$ROOT/scripts/templates/zed-delta-AGENTS.md"
UNINSTALL=0

personal_agents_md() {
  if [[ -f "$HOME/.config/zed/settings.json" ]]; then
    printf '%s\n' "$HOME/.config/zed/AGENTS.md"
  elif [[ -d "$HOME/Library/Application Support/Zed" ]]; then
    printf '%s\n' "$HOME/Library/Application Support/Zed/AGENTS.md"
  else
    printf '%s\n' "$HOME/.config/zed/AGENTS.md"
  fi
  printf '%s\n' "$HOME/.config/delta/AGENTS.md"
  if [[ -f "$HOME/Library/Application Support/delta/settings.json" ]]; then
    printf '%s\n' "$HOME/Library/Application Support/delta/AGENTS.md"
  fi
}

for arg in "$@"; do
  case "$arg" in
    --uninstall) UNINSTALL=1 ;;
    -h|--help)
      printf 'Usage: %s [--uninstall]\n' "$0"
      exit 0
      ;;
    *)
      printf 'error: unknown argument %s\n' "$arg" >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$SRC" ]]; then
  printf 'error: missing %s\n' "$SRC" >&2
  exit 1
fi

names=()
while IFS= read -r name; do
  [[ -n "$name" ]] && names+=("$name")
done < <(find "$SRC" -mindepth 1 -maxdepth 1 -exec basename {} \; | LC_ALL=C sort)

# Repo copy should stay hidden from Grok even after a global uninstall.
repo_ignore=("$ROOT/.agents/skills")
dest_ignore=()
for name in "${names[@]}"; do
  dest_ignore+=("$DEST/$name")
done

grok_ignore() {
  local action="$1"
  shift
  if [[ -f "$MERGE" && "$#" -gt 0 ]]; then
    python3 "$MERGE" "$GROK_CONFIG" "$action" "$@"
  fi
}

if [[ "$UNINSTALL" -eq 1 ]]; then
  printf 'Uninstall from %s\n' "$DEST"
  removed=0
  skipped=0
  for name in "${names[@]}"; do
    target="$DEST/$name"
    if [[ -L "$target" ]]; then
      link="$(readlink "$target")"
      case "$link" in
        "$SRC"/*|"$SRC")
          rm "$target"
          removed=$((removed + 1))
          ;;
        *)
          printf 'skip (foreign symlink): %s -> %s\n' "$target" "$link"
          skipped=$((skipped + 1))
          ;;
      esac
    elif [[ -e "$target" ]]; then
      printf 'skip (not our symlink): %s\n' "$target"
      skipped=$((skipped + 1))
    fi
  done
  grok_ignore remove "${dest_ignore[@]}"
  printf '\n==> personal AGENTS.md\n'
  while IFS= read -r agents_md; do
    python3 "$MERGE_AGENTS" remove "$agents_md"
  done < <(personal_agents_md)
  if [[ -f "$MARKER" ]]; then
    marker_root="$(cat "$MARKER")"
    if [[ "$marker_root" == "$ROOT" ]]; then
      rm -f "$MARKER"
    fi
  fi
  printf 'Removed %d symlink(s), skipped %d.\n' "$removed" "$skipped"
  printf 'Project copy at %s is unchanged.\n' "$SRC"
  exit 0
fi

mkdir -p "$DEST"
printf 'Repo:    %s\n' "$ROOT"
printf 'Install: %s\n' "$DEST"

linked=0
skipped=0
for name in "${names[@]}"; do
  from="$SRC/$name"
  to="$DEST/$name"
  if [[ -L "$to" ]]; then
    existing="$(readlink "$to")"
    if [[ "$existing" == "$from" ]]; then
      linked=$((linked + 1))
      continue
    fi
    printf 'skip (symlink exists): %s -> %s\n' "$to" "$existing"
    skipped=$((skipped + 1))
    continue
  fi
  if [[ -e "$to" ]]; then
    printf 'skip (path exists): %s\n' "$to"
    skipped=$((skipped + 1))
    continue
  fi
  ln -s "$from" "$to"
  linked=$((linked + 1))
done

printf '%s\n' "$ROOT" > "$MARKER"

printf '\n==> hide these copies from Grok Build\n'
grok_ignore add "${repo_ignore[@]}" "${dest_ignore[@]}"

printf '\n==> personal AGENTS.md (always-on default, like Grok enabling the plugin)\n'
while IFS= read -r agents_md; do
  python3 "$MERGE_AGENTS" add "$agents_md" "$TEMPLATE" "$ROOT"
done < <(personal_agents_md)

printf '\nLinked %d, skipped %d.\n' "$linked" "$skipped"
printf 'Zed and Zed Delta now load this pack in every project:\n'
printf '  skills:  %s\n' "$DEST"
printf '  rules:   personal AGENTS.md (Zed + Delta config dirs)\n'
printf 'Start a new agent thread so the instructions take effect.\n'
printf '\nCanonical commands (type these in Grok, Zed, and Delta):\n'
printf '  /agent-skills:spec  /agent-skills:plan  /agent-skills:build  /agent-skills:test\n'
printf '  /agent-skills:constraints  /agent-skills:review  /agent-skills:code-simplify\n'
printf '  /agent-skills:webperf  /agent-skills:ship\n'
printf 'Zed/Delta slash picker aliases: /spec /plan /build /test /constraints /code-review /code-simplify /webperf /ship\n'
printf 'Use /agent-skills:review (picker /code-review), not Delta /review.\n'
printf 'Re-run after pulling this repo.\n'
