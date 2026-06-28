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
    max_calls_per_run: int = 25
    max_records_per_run: int = 5000
    max_raw_bytes_per_run: int = 5_000_000
    min_poll_seconds: int = 300


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


@dataclass(frozen=True)
class SourceMatrixRow:
    asset_id: str
    canonical_symbol: str
    asset_type: str
    purpose: str
    selected_provider: str
    fallback_provider: str | None
    freshness: Freshness
    cost_tier: str
    requires_secret: bool
    dry_run: bool
    agent: str
    allowed_by_caps: bool
    cap_reason: str


def provider_from_record(record: dict[str, Any]) -> ProviderCapability:
    return ProviderCapability(
        provider=record["provider"],
        asset_types=tuple(record["asset_types"]),
        freshness=record["freshness"],
        cost_tier=record["cost_tier"],
        requires_secret=bool(record["requires_secret"]),
        preferred_for=tuple(record.get("preferred_for", [])),
        max_calls_per_run=int(record.get("max_calls_per_run", 25)),
        max_records_per_run=int(record.get("max_records_per_run", 5000)),
        max_raw_bytes_per_run=int(record.get("max_raw_bytes_per_run", 5_000_000)),
        min_poll_seconds=int(record.get("min_poll_seconds", 300)),
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


def choose_fallback_provider(
    asset: AssetMasterRecord,
    providers: list[ProviderCapability],
    selected: ProviderCapability,
) -> ProviderCapability | None:
    candidates = [
        provider
        for provider in providers
        if provider.provider != selected.provider and asset.asset_type in provider.asset_types
    ]
    mapped = [provider for provider in candidates if provider.provider in asset.provider_symbols]
    if mapped:
        candidates = mapped
    if not candidates:
        return None
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


def build_source_matrix(
    assets: list[AssetMasterRecord],
    providers: list[ProviderCapability],
    purpose: str,
    guard: CostGuard,
) -> list[SourceMatrixRow]:
    rows: list[SourceMatrixRow] = []
    for asset in assets:
        if asset.status not in {"active", "watchlist"}:
            continue
        selected = choose_provider(asset, providers, purpose)
        fallback = choose_fallback_provider(asset, providers, selected)
        allowed, reason = provider_within_caps(selected, guard)
        rows.append(
            SourceMatrixRow(
                asset_id=asset.asset_id,
                canonical_symbol=asset.canonical_symbol,
                asset_type=asset.asset_type,
                purpose=purpose,
                selected_provider=selected.provider,
                fallback_provider=fallback.provider if fallback else None,
                freshness=selected.freshness,
                cost_tier=selected.cost_tier,
                requires_secret=selected.requires_secret,
                dry_run=guard.dry_run,
                agent=_agent_for(asset, purpose),
                allowed_by_caps=allowed,
                cap_reason=reason,
            )
        )
    return rows[: guard.max_provider_calls]


def provider_within_caps(provider: ProviderCapability, guard: CostGuard) -> tuple[bool, str]:
    if provider.max_calls_per_run > guard.max_provider_calls:
        return False, "provider call cap exceeds run guard"
    if provider.max_records_per_run > guard.max_records:
        return False, "provider record cap exceeds run guard"
    if provider.max_raw_bytes_per_run > guard.max_raw_bytes:
        return False, "provider raw byte cap exceeds run guard"
    return True, "within configured caps"


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
