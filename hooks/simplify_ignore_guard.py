#!/usr/bin/env python3
"""Protect simplify-ignore blocks from Codex apply_patch edits."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple


START_MARKER = "simplify-ignore-start"
END_MARKER = "simplify-ignore-end"
COMMENT_OPENERS = ("//", "/*", "#", "<!--")


class GuardError(ValueError):
    """Raised when a patch cannot be checked safely."""


@dataclass
class Hunk:
    old_lines: List[str] = field(default_factory=list)
    new_lines: List[str] = field(default_factory=list)


@dataclass
class Operation:
    kind: str
    path: str
    hunks: List[Hunk] = field(default_factory=list)


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


def _flush_hunk(operation: Operation, hunk: Optional[Hunk]) -> None:
    if hunk is not None:
        operation.hunks.append(hunk)


def parse_patch(command: str) -> List[Operation]:
    """Parse the Codex apply_patch patch format conservatively."""
    lines = command.splitlines()
    if not lines or lines[0].strip() != "*** Begin Patch":
        raise GuardError("patch format is not recognized; protected files fail closed")

    operations = []
    operation = None
    hunk = None

    for line in lines[1:]:
        if line == "*** End Patch":
            _flush_hunk(operation, hunk)
            hunk = None
            operation = None
            break

        if line.startswith("*** Update File: "):
            _flush_hunk(operation, hunk)
            operation = Operation("update", line[len("*** Update File: ") :])
            operations.append(operation)
            hunk = None
            continue

        if line.startswith("*** Delete File: "):
            _flush_hunk(operation, hunk)
            operation = Operation("delete", line[len("*** Delete File: ") :])
            operations.append(operation)
            hunk = None
            continue

        if line.startswith("*** Add File: "):
            _flush_hunk(operation, hunk)
            operation = Operation("add", line[len("*** Add File: ") :])
            operations.append(operation)
            hunk = Hunk()
            continue

        if line.startswith("*** Move to: "):
            if operation is None or operation.kind != "update":
                raise GuardError("patch move directive is not recognized")
            operation.kind = "move"
            operation.path = operation.path + "\0" + line[len("*** Move to: ") :]
            continue

        if line.startswith("@@"):
            _flush_hunk(operation, hunk)
            if operation is None:
                raise GuardError("patch hunk has no target file")
            hunk = Hunk() if operation.kind in ("update", "move", "add") else None
            continue

        if line == "*** End of File":
            continue

        if operation is None:
            raise GuardError("patch contains an unrecognized operation")

        if operation.kind == "add":
            if not line.startswith("+"):
                raise GuardError("added file content is not recognized")
            hunk.new_lines.append(line[1:])
            continue

        if hunk is None:
            raise GuardError("file update has no patch hunk")
        if line.startswith(" "):
            content = line[1:]
            hunk.old_lines.append(content)
            hunk.new_lines.append(content)
        elif line.startswith("-"):
            hunk.old_lines.append(line[1:])
        elif line.startswith("+"):
            hunk.new_lines.append(line[1:])
        else:
            raise GuardError("patch line is not recognized")
    else:
        raise GuardError("patch is missing its end marker")

    return operations


def _find_sequence(lines: Sequence[str], sequence: Sequence[str], start: int) -> int:
    if not sequence:
        raise GuardError("patch hunk has no unchanged anchor; cannot analyze safely")

    matches = []
    final_start = len(lines) - len(sequence)
    for index in range(start, final_start + 1):
        if list(lines[index : index + len(sequence)]) == list(sequence):
            matches.append(index)
            if len(matches) > 1:
                raise GuardError("patch context is ambiguous; cannot analyze safely")

    if not matches:
        raise GuardError("patch context does not match the current file")
    return matches[0]


def apply_hunks(lines: Sequence[str], hunks: Sequence[Hunk]) -> List[str]:
    """Apply supported patch hunks in memory; never writes to disk."""
    result = list(lines)
    cursor = 0

    for hunk in hunks:
        if not hunk.old_lines:
            raise GuardError("patch hunk has no unchanged anchor; cannot analyze safely")
        index = _find_sequence(result, hunk.old_lines, cursor)
        result[index : index + len(hunk.old_lines)] = hunk.new_lines
        cursor = index + len(hunk.new_lines)

    return result


def _target_path(root: Path, patch_path: str) -> Optional[Path]:
    candidate = Path(patch_path)
    if not candidate.is_absolute():
        candidate = root / candidate

    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


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


def check_patch(command: str, cwd: str) -> Optional[str]:
    """Return a denial reason when a patch threatens a protected block."""
    try:
        operations = parse_patch(command)
        root = Path(cwd).resolve()

        for operation in operations:
            if operation.kind == "move":
                source, destination = operation.path.split("\0", 1)
                source_path = _target_path(root, source)
                destination_path = _target_path(root, destination)
                if source_path is not None and source_path.exists() and _read_marked_file(source_path)[1]:
                    raise GuardError(
                        "moving a file with simplify-ignore blocks cannot be analyzed safely"
                    )
                if destination_path is not None and destination_path.exists() and _read_marked_file(destination_path)[1]:
                    raise GuardError(
                        "moving onto a file with simplify-ignore blocks cannot be analyzed safely"
                    )
                continue

            target = _target_path(root, operation.path)
            if target is None or not target.exists() or operation.kind == "add":
                continue

            original_lines, protected_before = _read_marked_file(target)
            if not protected_before:
                continue

            if operation.kind == "delete":
                raise GuardError("deleting a file with simplify-ignore blocks is denied")

            updated_lines = apply_hunks(original_lines, operation.hunks)
            protected_after = parse_protected_blocks(updated_lines)
            if protected_after != protected_before:
                raise GuardError("patch changes or removes a simplify-ignore protected block")

    except (GuardError, OSError, UnicodeError) as error:
        return str(error)

    return None


def handle_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the Codex denial payload, or None when the call is allowed."""
    if event.get("hook_event_name") != "PreToolUse":
        return None
    if event.get("tool_name") != "apply_patch":
        return None

    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict) or not isinstance(tool_input.get("command"), str):
        reason = "apply_patch input is missing its command; protected files fail closed"
    else:
        reason = check_patch(tool_input["command"], str(event.get("cwd") or Path.cwd()))

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
