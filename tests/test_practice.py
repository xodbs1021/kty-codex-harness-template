import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("practice_probe", SOURCE / "scripts/practice_probe.py")
practice = importlib.util.module_from_spec(spec)
spec.loader.exec_module(practice)


class PracticeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kty-practice-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.sentinel = self.parent / "original-task.txt"
        self.sentinel.write_text("preserve original exercise")
        self.root = Path(practice.prepare(self.parent)["fixture"])

    def core(self, command, **kwargs):
        return subprocess.run([sys.executable, str(self.root / ".harness/harness.py"), command],
                              capture_output=True, text=True, **kwargs)

    def trace(self, name, **extra):
        payload = {"hook_event_name": name, "session_id": "synthetic-test-only", **extra}
        result = subprocess.run([sys.executable, str(self.root / ".harness/state/practice_hook_trace.py")],
                                input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_prepare_is_isolated_and_does_not_claim_untested_success(self):
        self.assertEqual(self.sentinel.read_text(), "preserve original exercise")
        self.assertTrue((self.root / ".git").is_dir())
        self.assertNotEqual(self.core("verify").returncode, 0)
        report = practice.report(self.root)
        self.assertEqual(report["recorded_callback_count"], 0)
        self.assertFalse(report["receipt_current"])
        self.assertTrue(report["review_fixture_unchanged"])
        self.assertTrue(report["dual_review_execution"].startswith("NOT_ASSESSED"))
        self.assertEqual((self.root / "practice_app.py").read_text(), practice.APP)

    def test_trace_forwards_real_core_and_report_checks_fresh_receipt(self):
        # Synthetic calls validate the adapter, not native Codex hook activation.
        self.assertEqual(self.trace("SessionStart"), {})
        (self.root / "probe_marker.py").write_text("VALUE = 1\n")
        self.assertEqual(self.trace("Stop")["decision"], "block")
        self.assertEqual(self.core("verify").returncode, 0)
        self.assertEqual(self.trace("Stop", stop_hook_active=True), {})
        report = practice.report(self.root)
        self.assertEqual(report["recorded_callback_count"], 3)
        self.assertTrue(report["receipt_current"])
        flow = report["hook_flows"][0]
        for field in ("session_start_observed", "stop_block_observed",
                      "stop_release_after_receipt", "automatic_continuation_observed"):
            self.assertTrue(flow[field])
        self.assertTrue(flow["baseline_file_present"])
        self.assertEqual(self.trace("Stop"), {})
        self.assertTrue(practice.report(self.root)["hook_flows"][0]["automatic_continuation_observed"])
        (self.root / "practice_app.py").write_text("changed review input\n")
        report = practice.report(self.root)
        self.assertFalse(report["receipt_current"])
        self.assertFalse(report["review_fixture_unchanged"])

    def test_trace_adapter_refuses_execution_outside_prepared_fixture(self):
        result = subprocess.run([sys.executable, str(SOURCE / "scripts/practice_hook_trace.py")],
                                input="{}", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
