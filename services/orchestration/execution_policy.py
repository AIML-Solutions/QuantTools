from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ExecutionKind = Literal["read_only", "local_backtest", "cloud_backtest", "cloud_write", "provider_network"]


@dataclass(frozen=True)
class ExecutionContext:
    lean_authenticated: bool = False
    docker_available: bool = False
    docker_accessible: bool = False
    cloud_backtests_enabled: bool = False
    cloud_writes_enabled: bool = False
    provider_network_enabled: bool = False
    max_estimated_cost_usd: float = 0.0


@dataclass(frozen=True)
class ExecutionRequest:
    kind: ExecutionKind
    name: str
    estimated_cost_usd: float = 0.0
    rationale: str = ""


@dataclass(frozen=True)
class ExecutionDecision:
    allowed: bool
    reason: str


def decide_execution(request: ExecutionRequest, context: ExecutionContext) -> ExecutionDecision:
    if request.estimated_cost_usd > context.max_estimated_cost_usd:
        return ExecutionDecision(False, "estimated cost exceeds configured maximum")

    if request.kind == "read_only":
        return ExecutionDecision(True, "read-only inspection is allowed")

    if request.kind == "local_backtest":
        if not context.docker_available:
            return ExecutionDecision(False, "local backtest requires Docker")
        if not context.docker_accessible:
            return ExecutionDecision(False, "Docker is installed but not accessible to this user")
        return ExecutionDecision(True, "local backtest is allowed")

    if request.kind == "cloud_backtest":
        if not context.lean_authenticated:
            return ExecutionDecision(False, "cloud backtest requires LEAN authentication")
        if not context.cloud_backtests_enabled:
            return ExecutionDecision(False, "cloud backtests require explicit approval")
        return ExecutionDecision(True, "cloud backtest is explicitly enabled")

    if request.kind == "cloud_write":
        if not context.cloud_writes_enabled:
            return ExecutionDecision(False, "cloud writes are disabled by default")
        return ExecutionDecision(True, "cloud writes are explicitly enabled")

    if request.kind == "provider_network":
        if not context.provider_network_enabled:
            return ExecutionDecision(False, "provider network calls are disabled by default")
        return ExecutionDecision(True, "provider network calls are explicitly enabled")

    return ExecutionDecision(False, "unknown execution kind")
