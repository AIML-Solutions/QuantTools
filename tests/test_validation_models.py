from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]
MODELS_PATH = ROOT / "services" / "validation" / "models.py"
spec = importlib.util.spec_from_file_location("validation_models", MODELS_PATH)
models = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(models)


class ValidationModelTests(unittest.TestCase):
    def test_asset_master_fixture_validates(self):
        records = json.loads((ROOT / "examples" / "asset_master.example.json").read_text())

        parsed = [models.AssetMasterRecord.model_validate(record) for record in records]

        self.assertEqual(parsed[0].asset_id, "etf:usa:SPY")
        self.assertEqual(parsed[1].session_rules, "continuous_24_7")

    def test_canonical_records_fixture_validates(self):
        records = json.loads((ROOT / "examples" / "canonical_records.example.json").read_text())

        bar = models.CanonicalMarketBar.model_validate(records["market_bar"])
        option = models.CanonicalOptionSnapshot.model_validate(records["option_snapshot"])

        self.assertEqual(bar.canonical_symbol, "SPY")
        self.assertEqual(option.right, "call")

    def test_rejects_asset_id_without_namespace(self):
        with self.assertRaises(ValidationError):
            models.AssetMasterRecord.model_validate(
                {
                    "asset_id": "SPY",
                    "asset_type": "etf",
                    "canonical_symbol": "SPY",
                    "venue": "usa_equity",
                }
            )

    def test_rejects_invalid_market_bar_range(self):
        with self.assertRaises(ValidationError):
            models.CanonicalMarketBar.model_validate(
                {
                    "asset_id": "etf:usa:SPY",
                    "canonical_symbol": "SPY",
                    "asset_type": "etf",
                    "provider": "example_provider",
                    "venue": "usa_equity",
                    "timestamp": "2026-06-28T14:30:00Z",
                    "timeframe": "1m",
                    "open": "100",
                    "high": "99",
                    "low": "101",
                    "close": "100",
                }
            )


if __name__ == "__main__":
    unittest.main()
