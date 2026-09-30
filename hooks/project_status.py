#!/usr/bin/env python3
"""At session start, suggest /agent-skills:setup-project in a git repository that is not set up. Read-only."""

import json
import os
from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def project_status(project: Path):
    """Return the SessionStart payload, or None when there is nothing to say."""
    agents = project / ".claude" / "agents"
    if not (project / ".git").exists() or project.resolve() == PACKAGE_ROOT:
        return None
    if (agents / "implementer.md").exists() and (agents / "reviewer.md").exists():
        return None
    return {
        "systemMessage": (
            "agent-skills: this project is not set up. Run /agent-skills:setup-project to install "
            "/spec, /plan, /build, /verify, /review and the implementer and reviewer agents."
        ),
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "This project has no implementer/reviewer agents in .claude/agents/. If the user asks for the "
                "agent-skills workflow, suggest /agent-skills:setup-project instead of improvising it."
            ),
        },
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
        result = project_status(Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or Path.cwd()))
    except Exception:  # Advisory hook: never block or disturb a session start.
        return 0
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
