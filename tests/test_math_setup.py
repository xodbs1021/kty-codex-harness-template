import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("math_setup", SOURCE / "template/.harness/math_setup.py")
math_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math_setup)


class MathSetupTest(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 11), "optional math installer needs Python 3.11")
    def test_registration_preserves_settings_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".codex").mkdir()
            path = root / ".codex/config.toml"
            initial = 'model = "existing"\napproval_policy = "never"\n'
            path.write_text(initial)
            math_setup.register(root)
            first = path.read_text()
            self.assertTrue(first.startswith(initial))
            math_setup.register(root)
            self.assertEqual(path.read_text(), first)
            path.write_text(first.replace('tool_timeout_sec = 30', 'tool_timeout_sec = 40'))
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                math_setup.register(root)
            self.assertEqual(path.read_bytes(), before)

    @unittest.skipIf(sys.version_info < (3, 11), "optional math installer needs Python 3.11")
    def test_registration_rejects_symlink_without_writing_external_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            external = root / "external.toml"
            external.write_text('model = "existing"\n')
            (root / ".codex").mkdir()
            (root / ".codex/config.toml").symlink_to(external)
            with self.assertRaises(ValueError):
                math_setup.register(root)
            self.assertEqual(external.read_text(), 'model = "existing"\n')

    def test_process_timeout_is_bounded_and_contains_diagnostic_stderr(self):
        with self.assertRaises(TimeoutError) as caught:
            math_setup.run([sys.executable, "-c",
                            'import sys,time; print("stage=thread", file=sys.stderr, flush=True); time.sleep(20)'],
                           timeout=0.3)
        self.assertIn("stage=thread", str(caught.exception))

    def test_failed_command_is_not_success(self):
        with self.assertRaises(RuntimeError):
            math_setup.run([sys.executable, "-c", "raise SystemExit(3)"])

    def test_unverified_install_cannot_register_or_start_mcp(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run([sys.executable, str(SOURCE / "scripts/install.py"), str(root)],
                           check=True, capture_output=True)
            for script in ("math_setup.py", "solver_setup.py"):
                result = subprocess.run([sys.executable, "-B", str(root / ".harness" / script), "register"],
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("mcp_servers", (root / ".codex/config.toml").read_text())

    @unittest.skipIf(sys.version_info < (3, 11), "optional math installer needs Python 3.11")
    def test_failed_recheck_invalidates_previous_mcp_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run([sys.executable, str(SOURCE / "scripts/install.py"), str(root)],
                           check=True, capture_output=True)
            base = root / ".harness/work/math-tools"
            base.mkdir(parents=True)
            broken = base / "broken-python"
            broken.write_text('#!/bin/sh\nexit 3\n')
            broken.chmod(0o755)
            state = base / "selected.json"
            state.write_text(json.dumps({"python": str(broken), "sdk_verified": True,
                                         "pins": math_setup.DIRECT + math_setup.MCP}))
            result = subprocess.run([sys.executable, "-B", str(root / ".harness/math_setup.py"), "install"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(json.loads(state.read_text())["sdk_verified"])
            self.assertFalse(json.loads((base / "latest-check.json").read_text())["passed"])


if __name__ == "__main__":
    unittest.main()
