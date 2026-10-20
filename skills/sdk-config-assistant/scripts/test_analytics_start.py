"""Tests for analytics_start.py: the Step 1a start record."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import analytics_start as a  # noqa: E402
import generate_sdk_patched as gen  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = a.main(argv)
    return code, buf.getvalue().splitlines()


class TestAnalyticsStart(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _args(self, **extra):
        argv = ["--profiles-dir", str(self.dir), "--run-id", "run-1", "--started-at", "2026-10-16T10:00:00Z",
                "--name", "Northwind Trading", "--domain", "www.northwindtrading.co.uk", "--tier", "Premium"]
        for k, v in extra.items():
            argv += ["--" + k.replace("_", "-"), v]
        return argv

    def _read(self, slug="northwind-trading"):
        return json.loads((self.dir / f"{slug}.analytics.json").read_text())

    def test_slug_matches_generator(self):
        for name in ("Northwind Trading", "Contoso & Co", "  Acme  Retail (UK) "):
            self.assertEqual(a.slugify(name), gen.slugify(name))

    def test_slug_only(self):
        code, out = _run(["--slug-only", "--name", "Northwind Trading"])
        self.assertEqual((code, out), (0, ["SLUG northwind-trading"]))

    def test_empty_name_gives_no_slug_and_no_file(self):
        for name in ("", "   ", "!!!"):
            code, out = _run(["--slug-only", "--name", name])
            self.assertEqual(code, 0)
            self.assertTrue(out[0].startswith("WARNING"), out)
            code, out = _run(["--profiles-dir", str(self.dir), "--run-id", "run-1",
                              "--started-at", "2026-10-16T10:00:00Z", "--name", name,
                              "--domain", "www.northwindtrading.co.uk", "--tier", "Premium"])
            self.assertEqual(code, 0)
            self.assertTrue(out[0].startswith("WARNING"), out)
            self.assertIn("name", out[0])
        self.assertEqual(list(self.dir.iterdir()), [])

    def test_creates_start_record(self):
        code, out = _run(self._args())
        self.assertEqual(code, 0)
        self.assertEqual(out[0], "OK northwind-trading")
        self.assertEqual(json.loads(out[1]), {})
        d = self._read()
        self.assertEqual(d["customerReference"], {"name": "Northwind Trading", "productionDomain": "www.northwindtrading.co.uk"})
        self.assertEqual(len(d["runHistory"]), 1)
        r = d["runHistory"][0]
        self.assertEqual((r["runId"], r["status"], r["subscriptionTier"], r["workflowMode"], r["action"]),
                         ("run-1", "started", "Premium", "new", "full_onboarding"))
        self.assertNotIn("operatorEmail", r)

    def test_second_call_updates_same_record_with_operator(self):
        _run(self._args())
        _run(self._args(operator_email="ops@acoustic.com"))
        d = self._read()
        self.assertEqual(len(d["runHistory"]), 1)
        self.assertEqual(d["runHistory"][0]["operatorEmail"], "ops@acoustic.com")
        self.assertEqual(d["operator"]["email"], "ops@acoustic.com")

    def test_keeps_earlier_runs_and_feedback(self):
        (self.dir / "northwind-trading.analytics.json").write_text(json.dumps({
            "profileSlug": "northwind-trading", "customerReference": {"name": "Northwind Trading", "productionDomain": "www.northwindtrading.co.uk"},
            "runHistory": [{"runId": "run-0", "workflowOutcome": "completed"}], "feedbackHistory": [{"id": "f1"}]}))
        _run(self._args())
        d = self._read()
        self.assertEqual([r["runId"] for r in d["runHistory"]], ["run-0", "run-1"])
        self.assertEqual(d["feedbackHistory"], [{"id": "f1"}])

    def test_never_downgrades_a_completed_record(self):
        (self.dir / "northwind-trading.analytics.json").write_text(json.dumps({
            "runHistory": [{"runId": "run-1", "status": "completed", "readiness": "production_ready"}]}))
        _run(self._args(operator_email="ops@acoustic.com"))
        r = self._read()["runHistory"][0]
        self.assertEqual((r["status"], r["readiness"]), ("completed", "production_ready"))

    def test_returns_manifest_meta(self):
        (self.dir / ".operator-cms-manifest.json").write_text(json.dumps(
            {"assets": {"northwind-trading": {"analytics": {"assetUuid": "u1", "assetRev": "r1"}}}}))
        _, out = _run(self._args())
        self.assertEqual(json.loads(out[1]), {"assetUuid": "u1", "assetRev": "r1"})

    def test_corrupt_file_is_replaced_not_fatal(self):
        (self.dir / "northwind-trading.analytics.json").write_text("{not json")
        code, out = _run(self._args())
        self.assertEqual((code, out[0]), (0, "OK northwind-trading"))

    def test_missing_dir_warns_and_exits_zero(self):
        code, out = _run(["--profiles-dir", str(self.dir / "nope"), "--run-id", "r", "--name", "X"])
        self.assertEqual(code, 0)
        self.assertTrue(out[0].startswith("WARNING"))


if __name__ == "__main__":
    unittest.main()
