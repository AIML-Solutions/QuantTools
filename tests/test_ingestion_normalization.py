from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.ingestion.normalization import (  # noqa: E402
    dedupe_market_bars,
    normalize_coingecko_market,
    normalize_stooq_daily_bar,
    validate_or_quarantine,
)
from services.ingestion.contracts import ProviderBatch, ProviderRequest  # noqa: E402
from services.validation.models import AssetMasterRecord, CanonicalMarketBar  # noqa: E402


def load_json(path: str):
    return json.loads((ROOT / path).read_text())


class IngestionNormalizationTests(unittest.TestCase):
    def test_stooq_daily_payload_normalizes_to_canonical_bar(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[0])
        row = load_json("examples/provider_payloads/stooq_daily_spy.json")

        bar = normalize_stooq_daily_bar(row, asset)

        self.assertEqual(bar.asset_id, "etf:usa:SPY")
        self.assertEqual(bar.provider, "stooq")
        self.assertEqual(bar.timeframe, "1d")
        self.assertEqual(str(bar.close), "602.50")

    def test_coingecko_payload_normalizes_to_canonical_bar(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[1])
        row = load_json("examples/provider_payloads/coingecko_bitcoin_market.json")
        as_of = datetime(2026, 6, 28, 14, 30, tzinfo=timezone.utc)

        bar = normalize_coingecko_market(row, asset, as_of)

        self.assertEqual(bar.asset_id, "crypto:spot:BTC-USD")
        self.assertEqual(bar.provider, "coingecko")
        self.assertEqual(bar.timeframe, "snapshot")
        self.assertEqual(str(bar.volume), "38000000000")

    def test_invalid_provider_payload_goes_to_quarantine(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[0])
        row = load_json("examples/provider_payloads/stooq_invalid_range.json")

        accepted, quarantine = validate_or_quarantine(
            source="stooq",
            record_type="market_bar",
            payload=row,
            factory=lambda payload: normalize_stooq_daily_bar(payload, asset),
            run_id="test-run-001",
        )

        self.assertIsNone(accepted)
        self.assertIsNotNone(quarantine)
        assert quarantine is not None
        self.assertEqual(quarantine.source, "stooq")
        self.assertEqual(quarantine.run_id, "test-run-001")
        self.assertIn("high must be greater", quarantine.reason)

    def test_valid_provider_payload_does_not_quarantine(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[0])
        row = load_json("examples/provider_payloads/stooq_daily_spy.json")

        accepted, quarantine = validate_or_quarantine(
            source="stooq",
            record_type="market_bar",
            payload=row,
            factory=lambda payload: normalize_stooq_daily_bar(payload, asset),
        )

        self.assertIsInstance(accepted, CanonicalMarketBar)
        self.assertIsNone(quarantine)

    def test_market_bar_dedupes_by_asset_timestamp_timeframe_provider(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[0])
        row = load_json("examples/provider_payloads/stooq_daily_spy.json")
        first = normalize_stooq_daily_bar(row, asset)
        second = normalize_stooq_daily_bar({**row, "Close": "603.00"}, asset)

        deduped, duplicates = dedupe_market_bars([first, second])

        self.assertEqual(duplicates, 1)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(str(deduped[0].close), "603.00")

    def test_provider_contracts_are_secret_free_by_default(self):
        asset = AssetMasterRecord.model_validate(load_json("examples/asset_master.example.json")[0])
        request = ProviderRequest(provider="stooq", assets=(asset,), purpose="fixture-test")
        batch = ProviderBatch(provider="stooq", records=(load_json("examples/provider_payloads/stooq_daily_spy.json"),), retrieved_at=request.requested_at)

        self.assertTrue(request.dry_run)
        self.assertEqual(batch.provider, "stooq")
        self.assertNotIn("api_key", batch.source_metadata)


if __name__ == "__main__":
    unittest.main()
