import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
CHECKER = SOURCE / "template/.agents/skills/google-styleguide/scripts/check_style.py"


class StyleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kty-style-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "task with spaces"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def run_style(self, env=None):
        return subprocess.run([sys.executable, "-B", str(CHECKER), "--root", str(self.root)],
                              capture_output=True, text=True, env=env)

    def isolated_path(self, gofmt=None):
        binaries = Path(self.temp.name) / "bin"
        binaries.mkdir(exist_ok=True)
        if not (binaries / "git").exists():
            (binaries / "git").symlink_to(shutil.which("git"))
        if gofmt:
            target = binaries / "gofmt"
            target.write_text(gofmt)
            target.chmod(0o755)
        return dict(os.environ, PATH=str(binaries))

    def test_no_go_is_not_applicable_even_without_gofmt(self):
        result = self.run_style(self.isolated_path())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NOT_APPLICABLE", result.stdout)

    def test_missing_gofmt_and_execution_error_are_unverified(self):
        (self.root / "a.go").write_text("package main\n")
        result = self.run_style(self.isolated_path())
        self.assertEqual(result.returncode, 2)
        self.assertIn("UNVERIFIED", result.stdout)
        result = self.run_style(self.isolated_path("#!/bin/sh\nexit 9\n"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("gofmt failed", result.stdout)

    @unittest.skipUnless(shutil.which("gofmt"), "actual gofmt unavailable")
    def test_real_gofmt_checks_tracked_and_new_files_without_modifying_them(self):
        file = self.root / "a space.go"
        file.write_text("package main\nfunc main(){println(1)}\n")
        before = file.read_bytes()
        result = self.run_style()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(file.read_bytes(), before)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["gofmt", "-w", str(file)], check=True)
        result = self.run_style()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)
        (self.root / "new.go").write_text("package main\nfunc newFunc(){println(2)}\n")
        self.assertEqual(self.run_style().returncode, 1)

    def test_vendor_ignored_and_external_symlink_are_not_read(self):
        for folder in ("vendor", "node_modules"):
            (self.root / folder).mkdir()
            (self.root / folder / "bad.go").write_text("not go")
        (self.root / ".gitignore").write_text("ignored.go\n")
        (self.root / "ignored.go").write_text("not go")
        self.assertIn("NOT_APPLICABLE", self.run_style().stdout)
        outside = Path(self.temp.name) / "outside.go"
        outside.write_text("not go")
        (self.root / "link.go").symlink_to(outside)
        result = self.run_style()
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stdout)

    @unittest.skipUnless(shutil.which("gofmt"), "actual gofmt unavailable")
    def test_installed_verify_and_stop_cannot_silently_skip_style(self):
        subprocess.run([sys.executable, str(SOURCE / "scripts/install.py"), str(self.root)],
                       check=True, capture_output=True)
        harness = self.root / ".harness/harness.py"

        def run(*args, event=None):
            return subprocess.run([sys.executable, str(harness), *args],
                                  input=json.dumps(event) if event else None,
                                  capture_output=True, text=True)

        start = {"hook_event_name": "SessionStart", "session_id": "style"}
        self.assertEqual(run("hook", event=start).returncode, 0)
        checks = self.root / ".harness/checks.json"
        checks.write_text(json.dumps({"checks": [{"name": "task", "argv": [
            sys.executable, "-c", "assert 2 + 2 == 4"]}]}))
        file = self.root / "main.go"
        file.write_text("package main\nfunc main(){println(1)}\n")
        self.assertEqual(run("verify").returncode, 1)
        receipt = self.root / ".harness/state/verification.json"
        self.assertFalse(json.loads(receipt.read_text())["passed"])
        stop = {"hook_event_name": "Stop", "session_id": "style"}
        self.assertEqual(json.loads(run("hook", event=stop).stdout)["decision"], "block")
        subprocess.run(["gofmt", "-w", str(file)], check=True)
        self.assertEqual(run("verify").returncode, 0)
        result = json.loads(receipt.read_text())
        self.assertEqual([r["name"] for r in result["results"]], ["harness:google-style", "task"])
        self.assertEqual(json.loads(run("hook", event=stop).stdout), {})
        # Missing checker invalidates a previously successful receipt.
        (self.root / ".agents/skills/google-styleguide/scripts/check_style.py").unlink()
        self.assertNotEqual(run("verify").returncode, 0)
        self.assertFalse(json.loads(receipt.read_text())["passed"])

    def test_bundled_reference_hashes_match_snapshot(self):
        root = CHECKER.parents[1] / "references"
        snapshot = json.loads((root / "snapshot.json").read_text())
        for name, expected in snapshot["files"].items():
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
