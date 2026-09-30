import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

import setup_project as sp

LINK = re.compile(r"(?:\]\(|`)((?:\.\./)+[\w./-]+\.md)")


def run(*argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = sp.main(list(argv))
    return status, out.getvalue() + err.getvalue()


def broken_links(root: Path) -> list[str]:
    return [f"{file}: {link}" for file in root.rglob("*.md") for link in LINK.findall(file.read_text())
            if not (file.parent / link).resolve().exists()]


class CatalogTest(unittest.TestCase):
    def test_core_skills_exist(self):
        self.assertEqual([n for n in sp.core_skills() if n not in sp.catalog_skills()], [])

    def test_agents_preload_only_core_skills(self):
        for agent in (sp.CATALOG / "agents").glob("*.md"):
            block = re.search(r"^skills:\n((?:  - .+\n)+)", agent.read_text(), re.MULTILINE)
            preloaded = {line.strip()[2:] for line in block.group(1).splitlines()}
            self.assertLessEqual(preloaded, set(sp.core_skills()), agent.name)

    def test_relative_links_resolve(self):
        self.assertEqual(broken_links(sp.CATALOG), [])

    def test_commands_use_project_names(self):
        # Only setup-project is a plugin skill; everything in the catalog runs as a project skill.
        prefixed = [f"{f}: {m}" for f in sp.CATALOG.rglob("*.md")
                    for m in re.findall(r"/agent-skills:[\w-]+", f.read_text()) if m != "/agent-skills:setup-project"]
        self.assertEqual(prefixed, [])


class SetupProjectTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name)
        self.claude = self.project / ".claude"

    def install(self) -> str:
        status, output = run("install", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        return output

    def installed(self) -> set[str]:
        return {p.parent.name for p in (self.claude / "skills").glob("*/SKILL.md")}

    def test_install_copies_core_agents_templates_and_references(self):
        self.install()
        self.assertEqual(self.installed(), set(sp.core_skills()))
        self.assertTrue((self.claude / "agents" / "implementer.md").exists())
        self.assertTrue((self.claude / "agents" / "reviewer.md").exists())
        self.assertEqual((self.project / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        self.assertTrue((self.claude / "references" / "security-checklist.md").exists())
        self.assertIn("explicitly invokes /spec.", (self.claude / "skills" / "spec" / "SKILL.md").read_text())

    def test_installed_links_resolve_inside_the_project(self):
        self.install()
        self.assertEqual(broken_links(self.claude / "skills"), [])

    def test_report_mentions_each_shared_reference_once(self):
        output = self.install()
        self.assertEqual(output.count("references/security-checklist.md"), 1, output)

    def test_install_never_overwrites_project_files(self):
        (self.project / "AGENTS.md").write_text("mine\n")
        adapted = self.claude / "skills" / "spec" / "SKILL.md"
        adapted.parent.mkdir(parents=True)
        adapted.write_text("adapted\n")
        output = self.install()
        self.assertEqual((self.project / "AGENTS.md").read_text(), "mine\n")
        self.assertEqual(adapted.read_text(), "adapted\n")
        self.assertIn("kept      skills/spec", output)

    def test_index_lists_only_skills_not_installed(self):
        self.install()
        index = (self.claude / "catalog.md").read_text()
        self.assertIn("- `performance-optimization`: ", index)
        self.assertNotIn("`test-driven-development`", index)

    def test_add_installs_skill_with_its_references_and_updates_index(self):
        self.install()
        status, output = run("add", "performance-optimization", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        self.assertIn("performance-optimization", self.installed())
        self.assertTrue((self.claude / "references" / "performance-checklist.md").exists())
        self.assertNotIn("`performance-optimization`", (self.claude / "catalog.md").read_text())

    def test_add_pulls_sibling_skills_the_shortcut_links_to(self):
        status, output = run("add", "review", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        self.assertEqual(self.installed(), {"review", "code-review-and-quality"})

    def test_add_unknown_skill_fails_without_writing(self):
        status, output = run("add", "no-such-skill", "--project", str(self.project))
        self.assertEqual(status, 1)
        self.assertIn("Unknown skill(s): no-such-skill", output)
        self.assertFalse(self.claude.exists())


if __name__ == "__main__":
    unittest.main()
