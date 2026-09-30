import unittest

from agent_bash_guard import handle_event


def bash(command, agent_type="implementer"):
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    if agent_type is not None:
        event["agent_type"] = agent_type
    return handle_event(event)


class GuardTest(unittest.TestCase):
    agent = "implementer"

    def assertDenied(self, *commands):
        for command in commands:
            self.assertIsNotNone(bash(command, self.agent), command)

    def assertAllowed(self, *commands):
        for command in commands:
            self.assertIsNone(bash(command, self.agent), command)


class ScopeTests(unittest.TestCase):
    def test_only_the_guarded_agents_are_checked(self):
        self.assertIsNone(bash("git commit -m done && git push", agent_type=None))
        self.assertIsNone(bash("git push", agent_type="general-purpose"))
        self.assertIsNotNone(bash("git push", agent_type="plugin:agent-skills:implementer"))

    def test_other_tools_are_ignored(self):
        self.assertIsNone(handle_event({"hook_event_name": "PreToolUse", "tool_name": "Edit", "agent_type": "reviewer"}))

    def test_denial_uses_pre_tool_use_contract(self):
        output = bash("git commit -m x")["hookSpecificOutput"]
        self.assertEqual((output["hookEventName"], output["permissionDecision"]), ("PreToolUse", "deny"))
        self.assertIn("orchestrating session", output["permissionDecisionReason"])

    def test_unparseable_or_missing_command_fails_closed(self):
        self.assertIn("cannot analyze", bash("echo 'unterminated")["hookSpecificOutput"]["permissionDecisionReason"])
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "agent_type": "reviewer", "tool_input": {}}
        self.assertIsNotNone(handle_event(event))


class ImplementerTests(GuardTest):
    def test_commits_and_history_changes(self):
        self.assertDenied("git commit -m x", "git -C app push origin main", "git rebase main", "git reset --hard",
                          "git reset HEAD~2")
        self.assertAllowed("git status", "git diff --stat", "git add src/app.ts", "git reset -- a.py", "git stash")

    def test_dependency_changes(self):
        self.assertDenied("npm install zod", "npm i -D vitest", "pnpm add zod", "yarn add zod", "uv add httpx",
                          "pip install requests", "python3 -m pip install requests", "uv pip install httpx",
                          "poetry add httpx", "cargo add serde", "go get example.com/x", "npm uninstall zod")
        self.assertAllowed("npm install", "npm ci", "yarn install", "uv sync", "pip install -r requirements.txt",
                           "pip install -e '.[dev]'")

    def test_migrations(self):
        self.assertDenied("npx prisma migrate deploy", "pnpm exec prisma migrate dev", "yarn prisma db push",
                          "uv run alembic upgrade head", "python manage.py migrate", "bundle exec rails db:migrate",
                          "npx knex migrate:latest", "npx typeorm migration:run -d src/data-source.ts")
        self.assertAllowed("npx prisma migrate dev --create-only --name init", "alembic revision --autogenerate",
                           "npx knex migrate:make add_users", "npx prisma generate")

    def test_wrappers_and_nesting(self):
        self.assertDenied("cd app && git commit -m x", "npm test; git push", "env CI=1 git commit -m x",
                          "bash -c 'git commit -m x'", "sh -lc \"npm install zod\"", "echo $(git commit -m x)",
                          "timeout 30 git push")

    def test_quoted_text_and_heredoc_bodies_are_not_commands(self):
        self.assertAllowed('grep -rn "git commit" docs', "cat <<'EOF' > notes.md\ngit push\nEOF")

    def test_may_write_files(self):
        self.assertAllowed("npx prettier --write src && sed -i '' 's/a/b/' x.ts && echo ok > out.txt")


class ReviewerTests(GuardTest):
    agent = "reviewer"

    def test_reading_and_running_checks(self):
        self.assertAllowed("git diff HEAD~1 -- src", "git log --oneline -5", "git branch --show-current",
                           "git stash list", "git config --get user.name", "npm test 2>&1 | tail -20",
                           "pytest -q > /dev/null", "grep -w id src/a.ts", "npx prettier --check src",
                           "sed -n '1,40p' src/a.ts", "find src -name '*.ts'")

    def test_repository_changes(self):
        self.assertDenied("git checkout main", "git stash", "git add .", "git restore src/a.ts", "git branch -D old")

    def test_file_writes(self):
        self.assertDenied("echo x > src/a.ts", "cat a >> b", "sed -i '' 's/a/b/' x.ts", "perl -pi -e 's/a/b/' x.ts",
                          "rm -rf dist", "mv a b", "npx prettier --write src", "npx eslint --fix src",
                          "gofmt -w .", "find . -name '*.orig' -delete", "xargs rm < files.txt")

    def test_implementer_rules_apply_too(self):
        self.assertDenied("npm install zod", "npx prisma migrate deploy")


if __name__ == "__main__":
    unittest.main()
