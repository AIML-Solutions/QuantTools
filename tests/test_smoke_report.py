from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.ingestion.network_smoke import SmokeResult  # noqa: E402
from services.ingestion.smoke_report import build_report  # noqa: E402


class SmokeReportTests(unittest.TestCase):
    def test_build_report_summarizes_results(self):
        report = build_report(
            [
                SmokeResult("one", skipped=False, ok=True, reason="ok", bytes_read=10),
                SmokeResult("two", skipped=True, ok=False, reason="disabled"),
                SmokeResult("three", skipped=False, ok=False, reason="missing key"),
            ]
        )

        self.assertEqual(report["summary"]["checks_total"], 3)
        self.assertEqual(report["summary"]["checks_ok"], 1)
        self.assertEqual(report["summary"]["checks_skipped"], 1)
        self.assertEqual(report["summary"]["checks_failed"], 1)
        self.assertIn("caveat", report)


if __name__ == "__main__":
    unittest.main()
