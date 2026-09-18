#!/usr/bin/env python3
"""Upsert or remove the managed agent-skills block in a personal AGENTS.md."""
from __future__ import annotations

import os
import sys

START = "<!-- agent-skills-pack:start -->"
END = "<!-- agent-skills-pack:end -->"


def render_block(template: str, pack_root: str) -> str:
    text = template.replace("__PACK_ROOT__", pack_root).strip() + "\n"
    if START not in text or END not in text:
        raise SystemExit("template is missing managed markers")
    return text


def upsert(existing: str, block: str) -> tuple[str, str]:
    start = existing.find(START)
    end = existing.find(END)
    if start != -1 and end != -1 and end > start:
        end += len(END)
        while end < len(existing) and existing[end] == "\n":
            end += 1
        new = existing[:start].rstrip() + "\n\n" + block + existing[end:].lstrip("\n")
        if not new.endswith("\n"):
            new += "\n"
        return new, "updated"
    if not existing.strip():
        return block, "created"
    body = existing.rstrip() + "\n\n" + block
    if not body.endswith("\n"):
        body += "\n"
    return body, "appended"


def strip_block(existing: str) -> tuple[str, str]:
    start = existing.find(START)
    end = existing.find(END)
    if start == -1 or end == -1 or end < start:
        return existing, "absent"
    end += len(END)
    while end < len(existing) and existing[end] == "\n":
        end += 1
    new = (existing[:start].rstrip() + "\n" + existing[end:].lstrip("\n")).strip()
    if new:
        new += "\n"
    return new, "removed"


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("add", "remove"):
        print(
            "usage: merge-agents-md.py add <dest> <template> <pack-root>\n"
            "       merge-agents-md.py remove <dest>",
            file=sys.stderr,
        )
        return 2

    action = sys.argv[1]
    dest = sys.argv[2]

    if action == "remove":
        if not os.path.exists(dest):
            print("skip (missing): %s" % dest)
            return 0
        text = open(dest, encoding="utf-8").read()
        new, status = strip_block(text)
        if status == "absent":
            print("no managed block: %s" % dest)
            return 0
        if new:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(new)
            print("removed block: %s" % dest)
        else:
            os.remove(dest)
            print("removed file: %s" % dest)
        return 0

    if len(sys.argv) != 5:
        print("usage: merge-agents-md.py add <dest> <template> <pack-root>", file=sys.stderr)
        return 2

    template_path, pack_root = sys.argv[3], sys.argv[4]
    block = render_block(open(template_path, encoding="utf-8").read(), pack_root)
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    existing = open(dest, encoding="utf-8").read() if os.path.exists(dest) else ""
    new, status = upsert(existing, block)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(new)
    print("%s %s" % (status, dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
