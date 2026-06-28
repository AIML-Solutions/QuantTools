from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from services.validation.models import AssetMasterRecord


Freshness = Literal["realtime", "near_realtime", "delayed", "daily", "historical", "event"]


@dataclass(frozen=True)
class ProviderCapability:
    provider: str
    asset_types: tuple[str, ...]
    freshness: Freshness
    cost_tier: Literal["free", "subscription", "unknown", "paid"]
    requires_secret: bool
    preferred_for: tuple[str, ...]


@dataclass(frozen=True)
class CostGuard:
    max_provider_calls: int = 25
    max_records: int = 5000
    max_raw_bytes: int = 5_000_000
    cloud_writes_enabled: bool = False
    network_enabled: bool = False
    dry_run: bool = True


@dataclass(frozen=True)
class ResearchTask:
    agent: str
    asset_id: str
    provider: str
    purpose: str
    freshness: Freshness
    dry_run: bool
    requires_secret: bool
    rationale: str


def provider_from_record(record: dict[str, Any]) -> ProviderCapability:
    return ProviderCapability(
        provider=record["provider"],
        asset_types=tuple(record["asset_types"]),
        freshness=record["freshness"],
        cost_tier=record["cost_tier"],
        requires_secret=bool(record["requires_secret"]),
        preferred_for=tuple(record.get("preferred_for", [])),
    )


def choose_provider(
    asset: AssetMasterRecord,
    providers: list[ProviderCapability],
    purpose: str,
) -> ProviderCapability:
    candidates = [provider for provider in providers if asset.asset_type in provider.asset_types]
    if not candidates:
        raise ValueError(f"no provider candidate for {asset.asset_id}")

    mapped = [provider for provider in candidates if provider.provider in asset.provider_symbols]
    if mapped:
        candidates = mapped

    preferred = [provider for provider in candidates if purpose in provider.preferred_for]
    if preferred:
        candidates = preferred

    return sorted(candidates, key=_provider_rank)[0]


def build_research_tasks(
    assets: list[AssetMasterRecord],
    providers: list[ProviderCapability],
    purpose: str,
    guard: CostGuard,
) -> list[ResearchTask]:
    tasks: list[ResearchTask] = []
    for asset in assets:
        if asset.status not in {"active", "watchlist"}:
            continue
        provider = choose_provider(asset, providers, purpose)
        tasks.append(
            ResearchTask(
                agent=_agent_for(asset, purpose),
                asset_id=asset.asset_id,
                provider=provider.provider,
                purpose=purpose,
                freshness=provider.freshness,
                dry_run=guard.dry_run,
                requires_secret=provider.requires_secret,
                rationale=f"{provider.provider} selected for {asset.asset_type} {purpose} under {provider.cost_tier} cost tier",
            )
        )
    return tasks[: guard.max_provider_calls]


def _provider_rank(provider: ProviderCapability) -> tuple[int, int, str]:
    cost_rank = {"free": 0, "subscription": 1, "unknown": 2, "paid": 3}[provider.cost_tier]
    secret_rank = 1 if provider.requires_secret else 0
    return (cost_rank, secret_rank, provider.provider)


def _agent_for(asset: AssetMasterRecord, purpose: str) -> str:
    if asset.asset_type in {"crypto", "token"} or "ledger" in asset.research_tags:
        return "onchain-and-crypto-scout"
    if purpose in {"options", "0dte"}:
        return "derivatives-scout"
    if asset.asset_type in {"rate", "macro"}:
        return "macro-rates-scout"
    return "market-data-scout"
