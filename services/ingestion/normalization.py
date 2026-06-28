from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, TypeVar

from pydantic import ValidationError

from services.validation.models import AssetMasterRecord, CanonicalMarketBar, QuarantineRecord


T = TypeVar("T")


def validate_or_quarantine(
    *,
    source: str,
    record_type: str,
    payload: dict[str, Any],
    factory: Callable[[dict[str, Any]], T],
    run_id: str | None = None,
) -> tuple[T | None, QuarantineRecord | None]:
    try:
        return factory(payload), None
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        return None, QuarantineRecord(
            source=source,
            record_type=record_type,
            reason=f"{type(exc).__name__}: {exc}",
            payload=payload,
            run_id=run_id,
        )


def normalize_stooq_daily_bar(row: dict[str, Any], asset: AssetMasterRecord) -> CanonicalMarketBar:
    timestamp = datetime.strptime(str(row["Date"]), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="stooq",
        venue=asset.venue,
        timestamp=timestamp,
        timeframe="1d",
        open=Decimal(str(row["Open"])),
        high=Decimal(str(row["High"])),
        low=Decimal(str(row["Low"])),
        close=Decimal(str(row["Close"])),
        volume=Decimal(str(row.get("Volume") or "0")),
        currency="USD",
    )


def normalize_coingecko_market(row: dict[str, Any], asset: AssetMasterRecord, as_of: datetime) -> CanonicalMarketBar:
    price = Decimal(str(row["current_price"]))
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="coingecko",
        venue=asset.venue,
        timestamp=as_of.astimezone(timezone.utc),
        timeframe="snapshot",
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal(str(row.get("total_volume") or "0")),
        currency="USD",
    )


def canonical_market_bar_key(record: CanonicalMarketBar) -> tuple[str, datetime, str, str]:
    return (record.asset_id, record.timestamp, record.timeframe, record.provider)


def dedupe_market_bars(records: list[CanonicalMarketBar]) -> tuple[list[CanonicalMarketBar], int]:
    by_key: dict[tuple[str, datetime, str, str], CanonicalMarketBar] = {}
    duplicates = 0
    for record in records:
        key = canonical_market_bar_key(record)
        if key in by_key:
            duplicates += 1
        by_key[key] = record
    return list(by_key.values()), duplicates
