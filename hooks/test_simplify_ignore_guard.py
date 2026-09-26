import tempfile
import unittest
from pathlib import Path

from simplify_ignore_guard import check_file_edit, check_patch, handle_event


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

    def patch(self, hunk):
        return "\n".join(
            [
                "*** Begin Patch",
                "*** Update File: example.py",
                "@@",
                *hunk,
                "*** End Patch",
            ]
        )

    def test_allows_changes_outside_protected_block(self):
        patch = self.patch(
            [
                " before()",
                "+safe_call()",
                " # simplify-ignore-start: perf-critical",
                " protected_call()",
                " # simplify-ignore-end",
                " after()",
            ]
        )

        self.assertIsNone(check_patch(patch, str(self.root)))
        self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_denies_changes_inside_protected_block(self):
        patch = self.patch(
            [
                " before()",
                " # simplify-ignore-start: perf-critical",
                "-protected_call()",
                "+simplified_call()",
                " # simplify-ignore-end",
                " after()",
            ]
        )

        reason = check_patch(patch, str(self.root))

        self.assertIsNotNone(reason)
        self.assertIn("protected", reason.lower())
        self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_denies_ambiguous_patch_for_protected_file(self):
        patch = self.patch(["+unanchored_change()"])

        reason = check_patch(patch, str(self.root))

        self.assertIsNotNone(reason)
        self.assertIn("analy", reason.lower())

    def test_denies_patch_missing_end_marker(self):
        patch = "\n".join(
            [
                "*** Begin Patch",
                "*** Update File: example.py",
                "@@",
                " before()",
            ]
        )

        reason = check_patch(patch, str(self.root))

        self.assertIsNotNone(reason)
        self.assertIn("end marker", reason.lower())

    def test_denies_unclosed_protected_marker(self):
        self.target.write_text(
            "# simplify-ignore-start\nprotected_call()\n", encoding="utf-8"
        )
        patch = self.patch([" protected_call()", "+changed_call()"])

        reason = check_patch(patch, str(self.root))

        self.assertIsNotNone(reason)
        self.assertIn("marker", reason.lower())

    def test_event_denial_uses_codex_pre_tool_contract(self):
        patch = self.patch(
            [
                " before()",
                " # simplify-ignore-start: perf-critical",
                "-protected_call()",
                "+simplified_call()",
                " # simplify-ignore-end",
                " after()",
            ]
        )

        result = handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {"command": patch},
                "cwd": str(self.root),
            }
        )

        self.assertEqual(result["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertEqual(
            result["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def test_ignores_unrelated_codex_tool_events(self):
        result = handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "cat example.py"},
                "cwd": str(self.root),
            }
        )

        self.assertIsNone(result)

    def test_allows_non_utf8_file_without_protected_markers(self):
        binary_target = self.root / "data.bin"
        binary_target.write_bytes(b"\xff\x00")
        patch = "\n".join(
            [
                "*** Begin Patch",
                "*** Update File: data.bin",
                "@@",
                "-old content",
                "+new content",
                "*** End Patch",
            ]
        )

        self.assertIsNone(check_patch(patch, str(self.root)))

    def test_marker_names_in_prose_are_not_protected_blocks(self):
        prose_target = self.root / "notes.md"
        prose_target.write_text(
            "The simplify-ignore-start token is documented here.\n", encoding="utf-8"
        )
        patch = "\n".join(
            [
                "*** Begin Patch",
                "*** Update File: notes.md",
                "@@",
                "-The simplify-ignore-start token is documented here.",
                "+The protected marker token is documented here.",
                "*** End Patch",
            ]
        )

        self.assertIsNone(check_patch(patch, str(self.root)))


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
