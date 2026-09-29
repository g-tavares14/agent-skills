import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import setup_project as sp


def run(*argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = sp.main(list(argv))
    return status, out.getvalue() + err.getvalue()


class CatalogIntegrityTest(unittest.TestCase):
    def test_core_skills_exist_in_catalog(self):
        catalog = sp.load_catalog()
        self.assertEqual([n for n in sp.load_core() if n not in catalog], [])

    def test_agents_preload_only_core_skills(self):
        core = set(sp.load_core())
        for agent in (sp.CATALOG / "agents").glob("*.md"):
            block = re.search(r"^skills:\n((?:  - .+\n)+)", agent.read_text(), re.MULTILINE)
            preloaded = {line.strip()[2:] for line in block.group(1).splitlines()}
            self.assertLessEqual(preloaded, core, agent.name)

    def test_relative_links_resolve_in_catalog(self):
        broken = []
        for file in sp.CATALOG.rglob("*.md"):
            for link in re.findall(r"(?:\]\(|`)((?:\.\./)+[\w./-]+\.md)", file.read_text()):
                if not (file.parent / link).resolve().exists():
                    broken.append(f"{file}: {link}")
        self.assertEqual(broken, [])

    def test_skill_names_are_unique(self):
        names = [p.parent.name for p in sp.CATALOG.glob("*/*/SKILL.md")]
        self.assertEqual(len(names), len(set(names)))


class SetupProjectTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name)
        self.claude = self.project / ".claude"

    def tearDown(self):
        self._tmp.cleanup()

    def install(self):
        status, output = run("install", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        return output

    def test_install_copies_core_agents_templates_and_references(self):
        self.install()
        installed = sp.installed_skills(self.project)
        self.assertEqual(installed, set(sp.load_core()))
        self.assertTrue((self.claude / "agents" / "implementer.md").exists())
        self.assertTrue((self.claude / "agents" / "reviewer.md").exists())
        self.assertTrue((self.project / "AGENTS.md").exists())
        self.assertEqual((self.project / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        self.assertTrue((self.claude / "references" / "security-checklist.md").exists())
        self.assertTrue((self.claude / "references" / "definition-of-done.md").exists())

    def test_installed_links_resolve_inside_the_project(self):
        self.install()
        broken = []
        for file in (self.claude / "skills").rglob("*.md"):
            for link in re.findall(r"(?:\]\(|`)((?:\.\./)+[\w./-]+\.md)", file.read_text()):
                if not (file.parent / link).resolve().exists():
                    broken.append(f"{file.relative_to(self.project)}: {link}")
        self.assertEqual(broken, [])

    def test_report_mentions_each_shared_reference_once(self):
        output = self.install()
        self.assertEqual(output.count("references/security-checklist.md"), 1, output)
        self.assertNotIn("kept      references/", output)

    def test_install_localizes_plugin_namespaced_shortcuts(self):
        self.install()
        spec = (self.claude / "skills" / "spec" / "SKILL.md").read_text()
        self.assertNotIn("/agent-skills:", spec)
        self.assertIn("explicitly invokes /spec.", spec)

    def test_install_never_overwrites_project_files(self):
        (self.project / "AGENTS.md").write_text("mine\n")
        adapted = self.claude / "skills" / "spec" / "SKILL.md"
        adapted.parent.mkdir(parents=True)
        adapted.write_text("---\nname: spec\n---\nadapted\n")
        output = self.install()
        self.assertEqual((self.project / "AGENTS.md").read_text(), "mine\n")
        self.assertEqual(adapted.read_text(), "---\nname: spec\n---\nadapted\n")
        self.assertIn("kept      skills/spec", output)

    def test_index_lists_only_skills_not_installed(self):
        self.install()
        index = (self.claude / "catalog.md").read_text()
        self.assertIn("`performance-optimization`", index)
        self.assertIn("## backend", index)
        self.assertNotIn("`test-driven-development`", index)

    def test_origin_records_each_installed_skill(self):
        self.install()
        record = json.loads((self.claude / "agent-skills.json").read_text())
        self.assertEqual(set(record["skills"]), set(sp.load_core()))
        self.assertEqual(record["skills"]["security-and-hardening"]["category"], "security")
        self.assertIn("repository", record["catalog"])

    def test_add_installs_skill_with_its_references_and_updates_index(self):
        self.install()
        status, output = run("add", "performance-optimization", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        self.assertTrue((self.claude / "skills" / "performance-optimization" / "SKILL.md").exists())
        self.assertTrue((self.claude / "references" / "performance-checklist.md").exists())
        self.assertNotIn("`performance-optimization`", (self.claude / "catalog.md").read_text())
        record = json.loads((self.claude / "agent-skills.json").read_text())
        self.assertIn("performance-optimization", record["skills"])

    def test_add_pulls_sibling_skills_the_shortcut_links_to(self):
        status, output = run("add", "review", "--project", str(self.project))
        self.assertEqual(status, 0, output)
        self.assertEqual(sp.installed_skills(self.project), {"review", "code-review-and-quality"})

    def test_add_unknown_skill_fails_without_writing(self):
        status, output = run("add", "no-such-skill", "--project", str(self.project))
        self.assertEqual(status, 1)
        self.assertIn("Unknown skill(s): no-such-skill", output)
        self.assertFalse(self.claude.exists())

    def test_refresh_forgets_removed_skills(self):
        self.install()
        for file in sorted((self.claude / "skills" / "code-simplification").rglob("*"), reverse=True):
            file.unlink() if file.is_file() else file.rmdir()
        (self.claude / "skills" / "code-simplification").rmdir()
        status, _ = run("refresh", "--project", str(self.project))
        self.assertEqual(status, 0)
        record = json.loads((self.claude / "agent-skills.json").read_text())
        self.assertNotIn("code-simplification", record["skills"])
        self.assertIn("`code-simplification`", (self.claude / "catalog.md").read_text())


if __name__ == "__main__":
    unittest.main()
