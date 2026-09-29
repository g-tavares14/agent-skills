#!/usr/bin/env python3
"""Copy catalog skills, shared references, and agent templates into a project's .claude/ directory.

Deterministic on purpose: it never chooses skills and never overwrites a file that already exists in the project,
because the project owns and adapts its copies.

Usage:
  setup_project.py install [--project DIR]          core skills, agents, AGENTS.md/CLAUDE.md, index
  setup_project.py add SKILL [SKILL ...] [--project DIR]
  setup_project.py refresh [--project DIR]          regenerate .claude/catalog.md and the origin record
  setup_project.py list [--project DIR]             catalog by category, marking installed skills
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
CATALOG = PACKAGE_ROOT / "catalog"
NON_SKILL_DIRS = {"agents", "references", "templates"}

SIBLING_SKILL = re.compile(r"\.\./([\w-]+)/SKILL\.md")
SHARED_REFERENCE = re.compile(r"\.\./\.\./references/([\w.-]+\.md)")
# In the catalog the shortcuts are plugin-namespaced; inside a project they are plain project skills.
PLUGIN_PREFIX = "/agent-skills:"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".txt"}


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    path: Path
    description: str


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    fields: dict[str, str] = {}
    if not match:
        return fields
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t", "#")):
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def load_catalog(catalog: Path = CATALOG) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    for skill_md in sorted(catalog.glob("*/*/SKILL.md")):
        category = skill_md.parent.parent.name
        if category in NON_SKILL_DIRS:
            continue
        meta = read_frontmatter(skill_md)
        name = meta.get("name", skill_md.parent.name)
        skills[name] = Skill(name, category, skill_md.parent, meta.get("description", ""))
    return skills


def load_core(catalog: Path = CATALOG) -> list[str]:
    lines = (catalog / "core.txt").read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def skill_links(skill: Skill) -> tuple[set[str], set[str]]:
    """Sibling skills and shared references a skill links to, so they travel with it."""
    siblings: set[str] = set()
    references: set[str] = set()
    for file in skill.path.rglob("*.md"):
        text = file.read_text(encoding="utf-8")
        siblings.update(SIBLING_SKILL.findall(text))
        references.update(SHARED_REFERENCE.findall(text))
    siblings.discard(skill.name)
    return siblings, references


def with_dependencies(names: list[str], catalog: dict[str, Skill]) -> list[str]:
    ordered: list[str] = []
    pending = list(names)
    while pending:
        name = pending.pop(0)
        if name in ordered:
            continue
        ordered.append(name)
        siblings, _ = skill_links(catalog[name])
        pending.extend(sorted(s for s in siblings if s in catalog))
    return ordered


def localize(directory: Path) -> None:
    for file in directory.rglob("*"):
        if file.is_file() and file.suffix in TEXT_SUFFIXES:
            text = file.read_text(encoding="utf-8")
            if PLUGIN_PREFIX in text:
                file.write_text(text.replace(PLUGIN_PREFIX, "/"), encoding="utf-8")


def copy_new_file(source: Path, target: Path, report: list[str], label: str) -> None:
    if target.exists():
        report.append(f"kept      {label} (already in the project)")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    report.append(f"added     {label}")


def install_skills(names: list[str], project: Path, catalog: dict[str, Skill], report: list[str]) -> list[str]:
    claude = project / ".claude"
    added: list[str] = []
    # Several skills share a checklist; report each one once, not once per skill that cites it.
    references: set[str] = set()
    for name in with_dependencies(names, catalog):
        skill = catalog[name]
        target = claude / "skills" / name
        if target.exists():
            report.append(f"kept      skills/{name} (already in the project)")
        else:
            shutil.copytree(skill.path, target)
            localize(target)
            added.append(name)
            report.append(f"added     skills/{name} ({skill.category})")
        references.update(skill_links(skill)[1])
    for ref in sorted(references):
        copy_new_file(CATALOG / "references" / ref, claude / "references" / ref, report, f"references/{ref}")
    return added


def package_origin() -> dict[str, str | None]:
    manifest = json.loads((PACKAGE_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    try:
        commit = subprocess.run(
            ["git", "-C", str(PACKAGE_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {"repository": manifest.get("repository"), "version": manifest.get("version"), "commit": commit}


def write_origin(project: Path, catalog: dict[str, Skill], added: list[str]) -> None:
    """Record where each installed skill came from, so later catalog changes can be diffed by hand."""
    path = project / ".claude" / "agent-skills.json"
    record = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"skills": {}}
    origin = package_origin()
    today = dt.date.today().isoformat()
    record["catalog"] = {"repository": origin["repository"]}
    for name in added:
        record["skills"][name] = {
            "category": catalog[name].category,
            "version": origin["version"],
            "commit": origin["commit"],
            "copied": today,
        }
    installed = installed_skills(project)
    for name in list(record["skills"]):
        if name not in installed:
            del record["skills"][name]
    record["skills"] = dict(sorted(record["skills"].items()))
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def installed_skills(project: Path) -> set[str]:
    skills_dir = project / ".claude" / "skills"
    return {p.parent.name for p in skills_dir.glob("*/SKILL.md")} if skills_dir.exists() else set()


def write_index(project: Path, catalog: dict[str, Skill]) -> None:
    installed = installed_skills(project)
    lines = [
        "# Skill catalog",
        "",
        "Catalog skills **not installed** in this project, by category. Generated by `setup-project`; do not edit.",
        "When a spec or plan needs one, suggest it to the owner and, if approved, add it with",
        "`/agent-skills:setup-project add <skill>` (requires the agent-skills plugin).",
    ]
    by_category: dict[str, list[Skill]] = {}
    for skill in catalog.values():
        if skill.name not in installed:
            by_category.setdefault(skill.category, []).append(skill)
    for category in sorted(by_category):
        lines += ["", f"## {category}", ""]
        lines += [f"- `{s.name}`: {s.description}" for s in sorted(by_category[category], key=lambda s: s.name)]
    if not by_category:
        lines += ["", "Every catalog skill is installed."]
    path = project / ".claude" / "catalog.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def unknown_names(names: list[str], catalog: dict[str, Skill]) -> list[str]:
    return [n for n in names if n not in catalog]


def cmd_install(project: Path, report: list[str]) -> None:
    catalog = load_catalog()
    added = install_skills(load_core(), project, catalog, report)
    for agent in sorted((CATALOG / "agents").glob("*.md")):
        copy_new_file(agent, project / ".claude" / "agents" / agent.name, report, f"agents/{agent.name}")
    for template in ("AGENTS.md", "CLAUDE.md"):
        copy_new_file(CATALOG / "templates" / template, project / template, report, template)
    write_origin(project, catalog, added)
    write_index(project, catalog)
    report.append("wrote     catalog.md, agent-skills.json")


def cmd_add(names: list[str], project: Path, report: list[str]) -> int:
    catalog = load_catalog()
    missing = unknown_names(names, catalog)
    if missing:
        print(f"Unknown skill(s): {', '.join(missing)}. Run `list` to see the catalog.", file=sys.stderr)
        return 1
    added = install_skills(names, project, catalog, report)
    write_origin(project, catalog, added)
    write_index(project, catalog)
    report.append("wrote     catalog.md, agent-skills.json")
    return 0


def cmd_refresh(project: Path, report: list[str]) -> None:
    catalog = load_catalog()
    write_origin(project, catalog, [])
    write_index(project, catalog)
    report.append("wrote     catalog.md, agent-skills.json")


def cmd_list(project: Path) -> None:
    catalog = load_catalog()
    installed = installed_skills(project)
    core = set(load_core())
    for category in sorted({s.category for s in catalog.values()}):
        print(f"{category}:")
        for skill in sorted((s for s in catalog.values() if s.category == category), key=lambda s: s.name):
            marks = ("installed" if skill.name in installed else "") + (" core" if skill.name in core else "")
            print(f"  {skill.name:40} {marks.strip()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["install", "add", "refresh", "list"])
    parser.add_argument("skills", nargs="*")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if args.command != "add" and args.skills:
        parser.error(f"`{args.command}` takes no skill names")
    if args.command == "add" and not args.skills:
        parser.error("`add` needs at least one skill name")

    report: list[str] = []
    status = 0
    if args.command == "install":
        cmd_install(project, report)
    elif args.command == "add":
        status = cmd_add(args.skills, project, report)
    elif args.command == "refresh":
        cmd_refresh(project, report)
    else:
        cmd_list(project)
    for line in report:
        print(line)
    return status


if __name__ == "__main__":
    sys.exit(main())
