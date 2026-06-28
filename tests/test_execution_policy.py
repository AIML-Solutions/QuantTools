from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.orchestration.execution_policy import (  # noqa: E402
    ExecutionContext,
    ExecutionRequest,
    decide_execution,
)


class ExecutionPolicyTests(unittest.TestCase):
    def test_read_only_checks_are_allowed(self):
        decision = decide_execution(ExecutionRequest(kind="read_only", name="lean whoami"), ExecutionContext())

        self.assertTrue(decision.allowed)

    def test_local_backtest_blocks_when_docker_requires_sudo(self):
        decision = decide_execution(
            ExecutionRequest(kind="local_backtest", name="baseline-strategy"),
            ExecutionContext(docker_available=True, docker_accessible=False),
        )

        self.assertFalse(decision.allowed)
        self.assertIn("not accessible", decision.reason)

    def test_cloud_backtest_requires_explicit_approval(self):
        decision = decide_execution(
            ExecutionRequest(kind="cloud_backtest", name="baseline-strategy"),
            ExecutionContext(lean_authenticated=True, cloud_backtests_enabled=False),
        )

        self.assertFalse(decision.allowed)
        self.assertIn("explicit approval", decision.reason)

    def test_cloud_write_blocks_by_default(self):
        decision = decide_execution(ExecutionRequest(kind="cloud_write", name="s3-write"), ExecutionContext())

        self.assertFalse(decision.allowed)

    def test_cost_cap_blocks_any_execution(self):
        decision = decide_execution(
            ExecutionRequest(kind="read_only", name="unexpected-cost", estimated_cost_usd=0.02),
            ExecutionContext(max_estimated_cost_usd=0.0),
        )

        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
