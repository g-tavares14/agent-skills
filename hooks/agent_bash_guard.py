#!/usr/bin/env python3
"""Hold the implementer and reviewer agents to their Bash rules (PreToolUse on Bash, subagent calls only).

implementer: no commits or history changes, no dependency changes, no applying migrations.
reviewer: the same, plus nothing that writes files or changes the repository.
The main session and other agents are never checked. Commands that cannot be parsed are denied.
"""

import json
from pathlib import Path
import re
import shlex
import sys

GUARDED_AGENTS = ("implementer", "reviewer")
OPERATORS = "();<>|&\n"
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")
SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
SHELLS = {"sh", "bash", "zsh", "dash"}
SAFE_TARGETS = {"/dev/null", "/dev/stdout", "/dev/stderr"}


class Violation(Exception):
    def __init__(self, category: str, command: str):
        super().__init__(category)
        self.category, self.command = category, command


def strip_heredocs(command: str) -> str:
    """Drop heredoc bodies: they are data fed to a command, not commands."""
    kept, pending = [], []
    for line in command.split("\n"):
        if pending:
            if line.strip() == pending[0]:
                pending.pop(0)
            continue
        kept.append(line)
        pending += [delimiter for _, delimiter in HEREDOC.findall(line)]
    if pending:
        raise ValueError("heredoc is not terminated")
    return "\n".join(kept)


def simple_commands(command: str):
    """Yield (argv, files written by redirection) for each simple command in a command line."""
    lexer = shlex.shlex(strip_heredocs(command), posix=True, punctuation_chars=OPERATORS)
    lexer.whitespace, lexer.whitespace_split = " \t\r", True
    tokens = list(lexer)
    argv, targets, i = [], [], 0
    while i < len(tokens):
        token = tokens[i]
        if token and set(token) <= set(OPERATORS):
            if "<" in token or ">" in token:
                if argv and argv[-1].isdigit():
                    argv.pop()  # the descriptor in `2>file`
                target = tokens[i + 1] if i + 1 < len(tokens) else ""
                if ">" in token and not (token.endswith("&") and (target.isdigit() or target == "-")):
                    targets.append(target)
                i += 2
                continue
            yield argv, targets
            argv, targets = [], []
        else:
            argv.append(token)
        i += 1
    yield argv, targets


WRAPPERS = {"sudo", "env", "command", "exec", "nohup", "time", "timeout", "xargs", "then", "do", "else", "if", "!"}
RUNNERS = {("npm", "exec"), ("pnpm", "exec"), ("pnpm", "dlx"), ("yarn", "dlx"), ("uv", "run"), ("poetry", "run"),
           ("bundle", "exec"), ("python", "-m"), ("python3", "-m")}


def commands_in(argv: list):
    """The command, then whatever a wrapper or package runner in front of it starts (`npx prisma`, `uv run`)."""
    while argv:
        name = Path(argv[0]).name
        if name in WRAPPERS or re.match(r"^[A-Za-z_]\w*=", argv[0]):
            argv = argv[1:]
            while argv and (argv[0].startswith("-") or argv[0][:1].isdigit()):
                argv = argv[1:]
            continue
        yield name, argv[1:]
        if name in ("npx", "bunx"):
            argv = argv[1:]
        elif (name, argv[1] if len(argv) > 1 else "") in RUNNERS:
            argv = argv[2:]
        elif name in ("pnpm", "yarn", "uv") and len(argv) > 1:
            argv = argv[1:]  # `pnpm prisma ...` runs a local binary; `uv pip install` is pip
        else:
            return
        while argv and argv[0].startswith("-"):
            argv = argv[1:]


def git_subcommand(args: list):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c") else 1
    return (args[i], args[i + 1:]) if i < len(args) else ("", [])


HISTORY = {"commit", "push", "pull", "merge", "rebase", "cherry-pick", "revert", "am", "filter-branch", "update-ref"}
READ_ONLY_GIT = {"status", "diff", "log", "show", "blame", "grep", "ls-files", "ls-tree", "rev-parse", "rev-list",
                 "cat-file", "merge-base", "describe", "shortlog", "show-ref", "for-each-ref", "check-ignore"}
# First argument that keeps a subcommand read-only ("" = no arguments).
LISTING_GIT = {"branch": {"", "--show-current", "-a", "-r", "-v", "--list"}, "tag": {"", "-l", "--list"},
               "stash": {"list", "show"}, "remote": {"", "-v", "show", "get-url"}, "reflog": {"", "show"},
               "config": {"--get", "--list", "-l"}}

DEPENDENCY_CHANGES = {"npm": {"uninstall", "remove", "rm", "update"}, "pnpm": {"add", "remove", "rm", "update"},
                      "yarn": {"add", "remove", "upgrade"}, "bun": {"add", "remove", "update"},
                      "uv": {"add", "remove"}, "poetry": {"add", "remove", "update"},
                      "cargo": {"add", "remove", "install"}, "go": {"get", "install"}, "pip": {"uninstall"}}
# Bare, these install what the lockfile or requirements file lists; with a package name they add one.
INSTALLS = {"npm": {"install", "i", "add"}, "pnpm": {"install", "i"}, "bun": {"install", "i"}, "pip": {"install"}}
FILE_FLAGS = {"-r", "--requirement", "-c", "--constraint", "-e", "--editable"}

MIGRATIONS = re.compile(r"""^(
    prisma\ (migrate\ (deploy|dev|reset|resolve)|db\ (push|execute))
  | drizzle-kit\ (migrate|push)
  | knex\ migrate:(latest|up|down|rollback)
  | sequelize(-cli)?\ db:migrate
  | typeorm\S*\ (migration:(run|revert)|schema:(sync|drop))
  | alembic\ (upgrade|downgrade|stamp)
  | (python[\d.]*\ )?manage\.py\ migrate
  | django-admin\ migrate
  | (rails|rake)\ db:(migrate|rollback|reset|drop|setup|schema:load)
)""", re.VERBOSE)

WRITE_COMMANDS = {"rm", "rmdir", "mv", "cp", "touch", "mkdir", "ln", "truncate", "dd", "chmod", "chown", "tee",
                  "patch", "rsync"}


def adds_packages(args: list) -> bool:
    skip = False
    for arg in args:
        if skip or arg in FILE_FLAGS:
            skip = not skip
            continue
        if not arg.startswith(("-", ".")):
            return True
    return False


def check_rules(agent: str, name: str, args: list) -> None:
    if name == "git":
        sub, rest = git_subcommand(args)
        if sub in HISTORY or sub == "reset" and any(a in ("--hard", "--soft") or "HEAD" in a or "~" in a
                                                    for a in rest):
            raise Violation("commits and history changes", f"git {sub}")
        if agent == "reviewer" and sub not in READ_ONLY_GIT and (rest[0] if rest else "") not in LISTING_GIT.get(sub, ()):
            raise Violation("changing the repository", f"git {sub}")

    tool = "pip" if re.fullmatch(r"pip[\d.]*", name) else name
    sub = args[0] if args else ""
    if sub in DEPENDENCY_CHANGES.get(tool, ()) or sub in INSTALLS.get(tool, ()) and adds_packages(args[1:]):
        raise Violation("dependency changes", f"{name} {sub}")

    words = [name] + [a for a in args if not a.startswith("-")]
    if MIGRATIONS.match(" ".join(Path(w).name for w in words)) and "--create-only" not in args:
        raise Violation("applying migrations", " ".join(words[:3]))

    if agent == "reviewer":
        flags = {a.split("=", 1)[0] for a in args}
        in_place = name in ("sed", "perl") and any(re.match(r"-[a-zA-Z]*i|--in-place", a) for a in args)
        if name in WRITE_COMMANDS or in_place or {"--write", "--fix"} & flags or \
                name == "find" and "-delete" in args or name in ("prettier", "gofmt") and "-w" in args:
            raise Violation("writing files", name)


def check_command(agent: str, command: str, depth: int = 0) -> None:
    if depth > 3:
        raise ValueError("command nests too deeply")
    for match in SUBSTITUTION.findall(command):
        check_command(agent, match[0] or match[1], depth + 1)
    for argv, targets in simple_commands(command):
        if agent == "reviewer" and any(t not in SAFE_TARGETS for t in targets):
            raise Violation("writing files", "> redirection")
        for name, args in commands_in(argv):
            check_rules(agent, name, args)
            if name in SHELLS and any(re.fullmatch(r"-[a-z]*c[a-z]*", a) for a in args):
                inner = [a for a in args if not a.startswith("-")]
                check_command(agent, inner[0] if inner else "", depth + 1)


def denial(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": "agent-skills guard: " + reason}}


def handle_event(event: dict):
    """Return the PreToolUse denial payload, or None when the call is allowed."""
    agent_type = event.get("agent_type")
    agent = next((a for a in GUARDED_AGENTS if isinstance(agent_type, str)
                  and (agent_type == a or agent_type.endswith(":" + a))), None)
    if event.get("hook_event_name") != "PreToolUse" or event.get("tool_name") != "Bash" or agent is None:
        return None
    command = (event.get("tool_input") or {}).get("command") if isinstance(event.get("tool_input"), dict) else None
    try:
        if not isinstance(command, str):
            raise ValueError("Bash input is not recognized")
        check_command(agent, command)
    except Violation as v:
        if agent == "implementer":
            return denial(f"the implementer may not run `{v.command}` ({v.category}). Do not work around it: stop "
                          "and put it in the report; the orchestrating session or the owner runs it after review.")
        return denial(f"the reviewer is read-only; `{v.command}` is not allowed ({v.category}). "
                      "Report it as a finding or as a step for the owner instead.")
    except Exception as error:  # fail closed: a command the guard cannot analyze is not allowed
        return denial(f"cannot analyze this command ({error}); rewrite it as simpler commands.")
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        result = handle_event(event) if isinstance(event, dict) else denial("hook input is not a JSON object.")
    except json.JSONDecodeError as error:
        result = denial(f"invalid hook input: {error}")
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
