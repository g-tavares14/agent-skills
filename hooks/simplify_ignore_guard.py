#!/usr/bin/env python3
"""Protect simplify-ignore blocks from Claude Code file edits (Edit, MultiEdit, Write)."""

import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple


START_MARKER = "simplify-ignore-start"
END_MARKER = "simplify-ignore-end"
COMMENT_OPENERS = ("//", "/*", "#", "<!--")


class GuardError(ValueError):
    """Raised when an edit cannot be checked safely."""


def parse_protected_blocks(lines: Sequence[str]) -> List[Tuple[str, ...]]:
    """Return the exact marked blocks, rejecting malformed marker pairs."""
    blocks = []
    active = None

    for line in lines:
        comment = line.lstrip()
        is_comment = any(comment.startswith(opener) for opener in COMMENT_OPENERS)
        has_start = is_comment and START_MARKER in comment
        has_end = is_comment and END_MARKER in comment

        if has_start:
            if active is not None:
                raise GuardError("nested simplify-ignore start marker")
            active = [line]
            if has_end:
                blocks.append(tuple(active))
                active = None
            continue

        if active is not None:
            active.append(line)

        if has_end:
            if active is None:
                raise GuardError("simplify-ignore end marker has no start marker")
            blocks.append(tuple(active))
            active = None

    if active is not None:
        raise GuardError("unclosed simplify-ignore start marker")

    return blocks


def _read_marked_file(path: Path) -> Tuple[List[str], List[Tuple[str, ...]]]:
    """Read a text file only when it contains a simplify-ignore marker."""
    content = path.read_bytes()
    if START_MARKER.encode("ascii") not in content and END_MARKER.encode("ascii") not in content:
        return [], []

    try:
        lines = content.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise GuardError("protected marker file is not valid UTF-8") from error
    return lines, parse_protected_blocks(lines)


CLAUDE_EDIT_TOOLS = ("Edit", "MultiEdit", "Write")


def _replace_text(text: str, old: Any, new: Any, replace_all: Any) -> str:
    """Apply one Claude Code string replacement in memory."""
    if not isinstance(old, str) or not isinstance(new, str) or not old:
        raise GuardError("edit input is not recognized; protected files fail closed")
    count = text.count(old)
    if count == 0:
        raise GuardError("edit text does not match the current file")
    if count > 1 and replace_all is not True:
        raise GuardError("edit text is ambiguous; cannot analyze safely")
    return text.replace(old, new) if replace_all is True else text.replace(old, new, 1)


def check_file_edit(tool_name: str, tool_input: Dict[str, Any], cwd: str) -> Optional[str]:
    """Return a denial reason when a Claude Code edit threatens a protected block."""
    try:
        file_path = tool_input.get("file_path")
        if not isinstance(file_path, str) or not file_path:
            raise GuardError("edit input is missing its file_path")

        target = Path(file_path)
        if not target.is_absolute():
            target = Path(cwd) / target
        if not target.exists():
            return None

        protected_before = _read_marked_file(target)[1]
        if not protected_before:
            return None

        if tool_name == "Write":
            content = tool_input.get("content")
            if not isinstance(content, str):
                raise GuardError("write input is missing its content")
        else:
            content = target.read_bytes().decode("utf-8")
            if tool_name == "Edit":
                edits = [tool_input]
            else:
                edits = tool_input.get("edits")
                if not isinstance(edits, list) or not edits:
                    raise GuardError("multi-edit input is missing its edits")
            for edit in edits:
                if not isinstance(edit, dict):
                    raise GuardError("edit input is not recognized; protected files fail closed")
                content = _replace_text(
                    content,
                    edit.get("old_string"),
                    edit.get("new_string"),
                    edit.get("replace_all"),
                )

        if parse_protected_blocks(content.splitlines()) != protected_before:
            raise GuardError("edit changes or removes a simplify-ignore protected block")

    except (GuardError, OSError, UnicodeError) as error:
        return str(error)

    return None


def handle_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the PreToolUse denial payload, or None when the call is allowed."""
    if event.get("hook_event_name") != "PreToolUse":
        return None
    tool_name = event.get("tool_name")
    if tool_name not in CLAUDE_EDIT_TOOLS:
        return None

    cwd = str(event.get("cwd") or Path.cwd())
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        reason = tool_name + " input is not recognized; protected files fail closed"
    else:
        reason = check_file_edit(tool_name, tool_input, cwd)

    if reason is None:
        return None

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "simplify-ignore guard: " + reason + ". Preserve marked code and retry."
            ),
        }
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("hook input must be a JSON object")
        result = handle_event(event)
    except (json.JSONDecodeError, ValueError) as error:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "simplify-ignore guard: invalid hook input: "
                + str(error),
            }
        }

    if result is not None:
        json.dump(result, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
