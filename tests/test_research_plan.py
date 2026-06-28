from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.orchestration.research_plan import (  # noqa: E402
    CostGuard,
    build_research_tasks,
    provider_from_record,
)
from services.validation.models import AssetMasterRecord  # noqa: E402


def load_json(path: str):
    return json.loads((ROOT / path).read_text())


class ResearchPlanTests(unittest.TestCase):
    def test_builds_dry_run_tasks_for_active_and_watchlist_assets(self):
        assets = [AssetMasterRecord.model_validate(record) for record in load_json("examples/asset_master.example.json")]
        providers = [provider_from_record(record) for record in load_json("examples/provider_catalog.example.json")]

        tasks = build_research_tasks(assets, providers, purpose="daily_baseline", guard=CostGuard(max_provider_calls=10))

        self.assertGreaterEqual(len(tasks), 5)
        self.assertTrue(all(task.dry_run for task in tasks))
        self.assertIn("market-data-scout", {task.agent for task in tasks})
        self.assertIn("onchain-and-crypto-scout", {task.agent for task in tasks})

    def test_prefers_options_sources_for_options_purpose(self):
        assets = [AssetMasterRecord.model_validate(record) for record in load_json("examples/asset_master.example.json")]
        providers = [provider_from_record(record) for record in load_json("examples/provider_catalog.example.json")]

        tasks = build_research_tasks(assets, providers, purpose="0dte", guard=CostGuard(max_provider_calls=10))
        spy_task = next(task for task in tasks if task.asset_id == "etf:usa:SPY")

        self.assertEqual(spy_task.agent, "derivatives-scout")
        self.assertIn(spy_task.provider, {"tradier", "lean"})

    def test_respects_provider_call_cap(self):
        assets = [AssetMasterRecord.model_validate(record) for record in load_json("examples/asset_master.example.json")]
        providers = [provider_from_record(record) for record in load_json("examples/provider_catalog.example.json")]

        tasks = build_research_tasks(assets, providers, purpose="daily_baseline", guard=CostGuard(max_provider_calls=2))

        self.assertEqual(len(tasks), 2)


if __name__ == "__main__":
    unittest.main()
