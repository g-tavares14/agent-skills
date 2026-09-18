#!/usr/bin/env python3
"""Merge paths into [skills].ignore in a Grok config.toml.

Does not rewrite other tables. Paths are stored as given; compare after
normalizing ~ and trailing slashes.
"""
from __future__ import annotations

import os
import re
import sys


def quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize(p: str) -> str:
    p = p.strip().strip('"').strip("'")
    if p.startswith("~/"):
        p = os.path.expanduser(p)
    return os.path.abspath(p).rstrip("/") if p else p


def parse_list(inner: str) -> list[str]:
    return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]


def render_ignore(items: list[str]) -> str:
    if not items:
        return "ignore = []\n"
    lines = "\n".join("  %s," % quote(i) for i in items)
    return "ignore = [\n%s\n]\n" % lines


def upsert_ignore(body: str, paths: list[str], remove: bool) -> tuple[str, bool]:
    pat = re.compile(r"^ignore\s*=\s*\[(.*?)\]", re.M | re.S)
    mm = pat.search(body)
    current = parse_list(mm.group(1)) if mm else []
    current_norm = {normalize(x): x for x in current if x}

    changed = False
    for path in paths:
        key = normalize(path)
        if remove:
            if key in current_norm:
                stored = current_norm.pop(key)
                current = [x for x in current if x != stored]
                changed = True
        else:
            if key not in current_norm:
                current.append(path)
                current_norm[key] = path
                changed = True

    rendered = render_ignore(current)
    if mm:
        body = pat.sub(rendered.rstrip("\n"), body, count=1)
        if not body.endswith("\n"):
            body += "\n"
    else:
        body = rendered + body
    return body, changed


def main() -> int:
    if len(sys.argv) < 4 or sys.argv[2] not in ("add", "remove"):
        print(
            "usage: merge-grok-skills-ignore.py <config.toml> add|remove <path> [path...]",
            file=sys.stderr,
        )
        return 2

    config_path = sys.argv[1]
    action = sys.argv[2]
    paths = sys.argv[3:]
    os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)
    text = open(config_path, encoding="utf-8").read() if os.path.exists(config_path) else ""

    comment = "# agent-skills — managed by scripts/install-zed.sh / install-grok.sh\n"
    block = comment + "[skills]\n" + render_ignore(paths if action == "add" else [])

    if "[skills]" not in text:
        if action == "remove":
            print("no [skills] section")
            return 0
        prefix = "" if not text or text.endswith("\n") else "\n"
        with open(config_path, "a", encoding="utf-8") as f:
            f.write(prefix + "\n" + block)
        print("appended [skills] ignore")
        return 0

    m = re.search(r"(?ms)^\[skills\]\n(.*?)(?=\n\[|\Z)", text)
    if not m:
        print("could not parse [skills]; leaving file unchanged", file=sys.stderr)
        return 1

    body, changed = upsert_ignore(m.group(1), paths, remove=(action == "remove"))
    if not changed:
        print("already configured")
        return 0

    new_text = text[: m.start()] + "[skills]\n" + body
    if not new_text.endswith("\n") and m.end() == len(text):
        new_text += "\n"
    else:
        new_text += text[m.end() :]
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("updated [skills] ignore (%s)" % action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
