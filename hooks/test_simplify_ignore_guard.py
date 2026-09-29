import tempfile
import unittest
from pathlib import Path

from simplify_ignore_guard import check_file_edit, handle_event


class SimplifyIgnoreGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.target = self.root / "example.py"
        self.original = "\n".join(
            [
                "before()",
                "# simplify-ignore-start: perf-critical",
                "protected_call()",
                "# simplify-ignore-end",
                "after()",
            ]
        )
        self.target.write_text(self.original, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_denies_edit_on_file_with_unclosed_marker(self):
        self.target.write_text(
            "# simplify-ignore-start\nprotected_call()\n", encoding="utf-8"
        )

        reason = check_file_edit(
            "Edit",
            {"file_path": str(self.target), "old_string": "protected_call()", "new_string": "x()"},
            str(self.root),
        )

        self.assertIsNotNone(reason)
        self.assertIn("marker", reason.lower())

    def test_denies_ambiguous_edit_on_protected_file(self):
        self.target.write_text(self.original + "\nbefore()\n", encoding="utf-8")

        reason = check_file_edit(
            "Edit",
            {"file_path": str(self.target), "old_string": "before()", "new_string": "setup()"},
            str(self.root),
        )

        self.assertIn("ambiguous", reason)

    def test_denial_uses_pre_tool_use_contract(self):
        result = self.claude_event(
            "Edit", {"old_string": "protected_call()", "new_string": "simplified()"}
        )

        self.assertEqual(result["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertIn("simplify-ignore guard", result["hookSpecificOutput"]["permissionDecisionReason"])

    def test_ignores_unrelated_tool_events(self):
        result = handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "cat example.py"},
                "cwd": str(self.root),
            }
        )

        self.assertIsNone(result)

    def test_ignores_apply_patch_events(self):
        result = handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {"command": "not a patch"},
                "cwd": str(self.root),
            }
        )

        self.assertIsNone(result)

    def test_allows_edit_on_non_utf8_file_without_markers(self):
        binary_target = self.root / "data.bin"
        binary_target.write_bytes(b"\xff\x00")

        reason = check_file_edit(
            "Edit",
            {"file_path": str(binary_target), "old_string": "old", "new_string": "new"},
            str(self.root),
        )

        self.assertIsNone(reason)

    def test_marker_names_in_prose_are_not_protected_blocks(self):
        prose_target = self.root / "notes.md"
        prose_target.write_text(
            "The simplify-ignore-start token is documented here.\n", encoding="utf-8"
        )

        reason = check_file_edit(
            "Edit",
            {
                "file_path": str(prose_target),
                "old_string": "The simplify-ignore-start token",
                "new_string": "The protected marker token",
            },
            str(self.root),
        )

        self.assertIsNone(reason)

    def claude_event(self, tool_name, tool_input):
        return handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": tool_name,
                "tool_input": {"file_path": str(self.target), **tool_input},
                "cwd": str(self.root),
            }
        )

    def test_claude_edit_outside_protected_block_is_allowed(self):
        result = self.claude_event(
            "Edit", {"old_string": "before()", "new_string": "setup()"}
        )

        self.assertIsNone(result)
        self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_claude_edit_inside_protected_block_is_denied(self):
        result = self.claude_event(
            "Edit", {"old_string": "protected_call()", "new_string": "simplified()"}
        )

        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_claude_edit_removing_marker_is_denied(self):
        result = self.claude_event(
            "Edit",
            {"old_string": "# simplify-ignore-end\n", "new_string": ""},
        )

        self.assertIsNotNone(result)

    def test_claude_edit_with_unmatched_text_fails_closed(self):
        reason = check_file_edit(
            "Edit",
            {"file_path": str(self.target), "old_string": "missing()", "new_string": "x"},
            str(self.root),
        )

        self.assertIn("does not match", reason)

    def test_claude_multi_edit_checks_every_edit(self):
        result = self.claude_event(
            "MultiEdit",
            {
                "edits": [
                    {"old_string": "before()", "new_string": "setup()"},
                    {"old_string": "protected_call()", "new_string": "simplified()"},
                ]
            },
        )

        self.assertIsNotNone(result)

    def test_claude_write_preserving_block_is_allowed(self):
        content = self.original.replace("after()", "teardown()")

        self.assertIsNone(self.claude_event("Write", {"content": content}))

    def test_claude_write_dropping_block_is_denied(self):
        self.assertIsNotNone(self.claude_event("Write", {"content": "rewritten()\n"}))

    def test_claude_edit_on_unmarked_file_is_allowed(self):
        plain = self.root / "plain.py"
        plain.write_text("value = 1\n", encoding="utf-8")

        reason = check_file_edit(
            "Edit",
            {"file_path": str(plain), "old_string": "absent", "new_string": "x"},
            str(self.root),
        )

        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()
