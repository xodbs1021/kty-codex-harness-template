import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SOURCE = Path(__file__).resolve().parents[1]
INSTALLER = SOURCE / "scripts/install.py"


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kty-harness-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "task workspace"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write("app.py", "value = 1\n")
        self.write(".gitignore", "__pycache__/\n")

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def install(self, *args, success=True):
        result = subprocess.run([sys.executable, str(INSTALLER), str(self.root), *args],
                                capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def command(self, *args, success=True, stdin=None, env=None):
        result = subprocess.run([sys.executable, str(self.root / ".harness/harness.py"), *args],
                                input=stdin, capture_output=True, text=True, env=env)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def checks(self, code="pass", timeout=5):
        self.write(".harness/checks.json", json.dumps({"checks": [{"name": "test",
                   "argv": [sys.executable, "-c", code], "timeout_seconds": timeout}]}))

    def event(self, event, session="first", **extra):
        return json.loads(self.command("hook", stdin=json.dumps({
            "hook_event_name": event, "session_id": session, **extra,
        })).stdout)

    def receipt(self):
        return json.loads((self.root / ".harness/state/verification.json").read_text())

    def test_install_preserves_project_and_is_idempotent(self):
        self.write("AGENTS.md", "# Existing project instructions\n")
        self.install()
        self.assertIn("# Existing project instructions", (self.root / "AGENTS.md").read_text())
        self.write(".harness/project-profile.md", "project-specific facts")
        self.checks()
        first = (self.root / "AGENTS.md").read_bytes()
        self.install()
        self.assertEqual(first, (self.root / "AGENTS.md").read_bytes())
        self.assertEqual((self.root / ".harness/project-profile.md").read_text(), "project-specific facts")
        self.assertEqual(len(json.loads((self.root / ".harness/checks.json").read_text())["checks"]), 1)
        hooks = json.loads((self.root / ".codex/hooks.json").read_text())["hooks"]
        self.assertEqual(len(hooks["Stop"]), 1)

    def test_existing_config_and_hooks_are_preserved(self):
        self.write(".codex/config.toml", 'model = "existing-model"\n[features]\nhooks = true\n')
        existing = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "existing-hook"}]}]}}
        self.write(".codex/hooks.json", json.dumps(existing))
        self.install()
        self.assertIn("existing-model", (self.root / ".codex/config.toml").read_text())
        hooks = json.loads((self.root / ".codex/hooks.json").read_text())["hooks"]["Stop"]
        self.assertEqual(hooks[0], existing["hooks"]["Stop"][0])
        self.assertEqual(len(hooks), 2)

    def test_no_hooks_does_not_touch_existing_hook_configuration(self):
        self.write(".codex/hooks.json", '{"hooks": {}}\n')
        self.install("--no-hooks")
        self.assertEqual((self.root / ".codex/hooks.json").read_text(), '{"hooks": {}}\n')

    def test_conflicting_managed_file_aborts_before_writes(self):
        self.write(".harness/principles.md", "my existing principles")
        self.install(success=False)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / ".codex/config.toml").exists())
        self.assertEqual((self.root / ".harness/principles.md").read_text(), "my existing principles")

    def test_changed_installed_file_is_not_overwritten(self):
        self.install()
        self.write(".harness/harness.py", "user modification")
        self.install(success=False)
        self.assertEqual((self.root / ".harness/harness.py").read_text(), "user modification")

    def test_symlink_destination_cannot_write_outside_workspace(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / ".codex").symlink_to(outside, target_is_directory=True)
        self.install(success=False)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_parent_file_conflict_aborts_before_writes(self):
        self.write(".harness", "not a directory")
        self.install(success=False)
        self.assertFalse((self.root / ".codex").exists())

    def test_broken_agents_markers_abort_before_writes(self):
        self.write("AGENTS.md", "<!-- kty-codex-harness:start -->\n")
        self.install(success=False)
        self.assertFalse((self.root / ".codex/config.toml").exists())

    def test_nested_git_directory_is_rejected(self):
        child = self.root / "child"
        child.mkdir()
        result = subprocess.run([sys.executable, str(INSTALLER), str(child)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(child.iterdir()), [])

    def test_empty_checks_fail_and_do_not_issue_passing_receipt(self):
        self.install()
        self.command("verify", success=False)
        self.assertFalse(self.receipt()["passed"])

    def test_success_receipt_and_subsequent_failure_invalidate_previous_pass(self):
        self.install()
        self.checks()
        self.command("verify")
        self.assertTrue(self.receipt()["passed"])
        self.checks("raise SystemExit(7)")
        self.command("verify", success=False)
        self.assertFalse(self.receipt()["passed"])
        self.assertEqual(self.receipt()["results"][0]["exit_code"], 7)

    def test_missing_command_and_timeout_fail(self):
        self.install()
        self.write(".harness/checks.json", '{"checks":[{"name":"missing","argv":["/missing-executable"]}]}')
        self.command("verify", success=False)
        self.assertFalse(self.receipt()["passed"])
        self.checks("import time; time.sleep(2)", timeout=1)
        self.command("verify", success=False)
        self.assertFalse(self.receipt()["passed"])

    def test_command_argv_is_not_interpreted_by_shell(self):
        self.install()
        marker = self.root / "shell-marker"
        self.write(".harness/checks.json", json.dumps({"checks": [{"name": "literal",
                   "argv": [sys.executable, "-c", "import sys; assert sys.argv[1].startswith('$(touch')",
                            "$(touch " + str(marker) + ")"]}]}))
        self.command("verify")
        self.assertFalse(marker.exists())

    def test_timeout_also_stops_descendant_processes(self):
        self.install()
        child = "import time; from pathlib import Path; time.sleep(2); Path('late-output').write_text('orphan')"
        parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); time.sleep(5)"
        self.checks(parent, timeout=1)
        self.command("verify", success=False)
        time.sleep(1.3)
        self.assertFalse((self.root / "late-output").exists())

    def test_files_changed_during_verification_fail(self):
        self.install()
        self.checks("from pathlib import Path; Path('app.py').write_text('value = 3')")
        self.command("verify", success=False)
        self.assertFalse(self.receipt()["passed"])

    def test_hooks_require_fresh_receipt_after_tracked_or_untracked_changes(self):
        self.install()
        self.checks()
        self.assertEqual(self.event("SessionStart"), {})
        self.assertEqual(self.event("Stop"), {})
        self.write("app.py", "value = 2\n")
        self.assertEqual(self.event("Stop")["decision"], "block")
        self.command("verify")
        self.assertEqual(self.event("Stop"), {})
        self.write("new.py", "new = True\n")
        self.assertEqual(self.event("Stop")["decision"], "block")
        self.assertIn("systemMessage", self.event("Stop", stop_hook_active=True))

    def test_receipt_and_work_notes_do_not_make_themselves_stale(self):
        self.install()
        self.checks()
        self.event("SessionStart")
        self.write("app.py", "value = 2\n")
        self.command("verify")
        self.write(".harness/work/progress.md", "progress")
        self.assertEqual(self.event("Stop"), {})

    def test_sessions_and_resume_keep_separate_baselines(self):
        self.install()
        self.event("SessionStart", session="first")
        self.write("app.py", "value = 2\n")
        self.event("SessionStart", session="second")
        self.assertEqual(self.event("Stop", session="second"), {})
        self.event("SessionStart", session="first")
        self.assertEqual(self.event("Stop", session="first")["decision"], "block")

    def test_tracked_deletion_and_symlink_change_invalidate_receipt(self):
        self.install()
        self.checks()
        subprocess.run(["git", "-C", str(self.root), "add", "app.py"], check=True)
        before = self.command("fingerprint").stdout
        (self.root / "app.py").unlink()
        self.assertNotEqual(before, self.command("fingerprint").stdout)
        (self.root / "app.py").symlink_to("unreadable-outside-file")
        before = self.command("fingerprint").stdout
        (self.root / "app.py").unlink()
        (self.root / "app.py").symlink_to("different-outside-file")
        self.assertNotEqual(before, self.command("fingerprint").stdout)

    def test_launcher_pins_model_and_effort_without_security_overrides(self):
        self.install()
        fake = self.root / "bin/codex"
        fake.parent.mkdir()
        fake.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        fake.chmod(0o755)
        env = dict(os.environ, PATH=str(fake.parent) + os.pathsep + os.environ["PATH"])
        result = self.command("codex", "--", "-m different-model", env=env)
        args = json.loads(result.stdout)
        self.assertEqual(args[:6], ["--cd", str(self.root.resolve()), "--model", "gpt-6.1-sol", "--config",
                                   'model_reasoning_effort="xhigh"'])
        self.assertEqual(args[-2:], ["--", "-m different-model"])
        self.assertEqual(args[6:-2:2], ["--config"] * 8)
        values = dict(item.split("=", 1) for item in args[7:-2:2])
        for role in ("planner", "developer", "reviewer", "auditor"):
            path = Path(json.loads(values["agents.kty_" + role + ".config_file"]))
            self.assertTrue(path.is_file())
            content = path.read_text()
            self.assertIn('model = "gpt-6.1-sol"', content)
            self.assertIn('model_reasoning_effort = "xhigh"', content)
            if role != "developer":
                self.assertIn('sandbox_mode = "read-only"', content)


if __name__ == "__main__":
    unittest.main()
