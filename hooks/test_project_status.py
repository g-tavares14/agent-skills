import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import project_status
from project_status import PACKAGE_ROOT, project_status as status


class ProjectStatusTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name)
        (self.project / ".git").mkdir()

    def test_suggests_setup_in_a_project_without_the_agents(self):
        result = status(self.project)
        self.assertIn("/agent-skills:setup-project", result["systemMessage"])
        self.assertEqual(result["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_silent_in_a_set_up_project(self):
        agents = self.project / ".claude" / "agents"
        agents.mkdir(parents=True)
        (agents / "implementer.md").write_text("x")
        (agents / "reviewer.md").write_text("x")
        self.assertIsNone(status(self.project))

    def test_silent_outside_git_repositories_and_in_the_plugin_itself(self):
        (self.project / ".git").rmdir()
        self.assertIsNone(status(self.project))
        self.assertIsNone(status(PACKAGE_ROOT))

    def run_main(self, stdin: str) -> str:
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.project)}), \
                mock.patch("sys.stdin", io.StringIO(stdin)), redirect_stdout(out):
            self.assertEqual(project_status.main(), 0)
        return out.getvalue()

    def test_main_uses_the_project_dir_and_never_fails(self):
        self.assertIn("setup-project", json.loads(self.run_main("{}"))["systemMessage"])
        self.assertEqual(self.run_main("not json"), "")


if __name__ == "__main__":
    unittest.main()
