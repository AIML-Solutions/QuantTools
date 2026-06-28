from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.ingestion.network_smoke import (  # noqa: E402
    ENABLE_NETWORK_ENV,
    default_smoke_requests,
    network_enabled,
    run_default_smokes,
)


class NetworkSmokeTests(unittest.TestCase):
    def test_network_disabled_by_default(self):
        self.assertFalse(network_enabled({}))
        self.assertFalse(network_enabled({ENABLE_NETWORK_ENV: "0"}))
        self.assertTrue(network_enabled({ENABLE_NETWORK_ENV: "1"}))

    def test_default_smokes_skip_without_network_flag(self):
        results = run_default_smokes(enabled=False)

        self.assertGreaterEqual(len(results), 4)
        self.assertTrue(all(result.skipped for result in results))
        self.assertTrue(all(not result.ok for result in results))

    def test_default_smokes_are_no_auth_public_sources(self):
        providers = {request.provider for request in default_smoke_requests()}

        self.assertEqual(
            providers,
            {"sec_edgar", "treasury_fiscal_data", "coinbase_public", "kraken_public"},
        )
