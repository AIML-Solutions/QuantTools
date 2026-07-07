from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, TypeVar

from pydantic import ValidationError

from services.validation.models import AssetMasterRecord, CanonicalMarketBar, QuarantineRecord, RecordQuality


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
        quality=RecordQuality(effective_at=timestamp, provider_timestamp=timestamp),
    )


def normalize_coingecko_market(row: dict[str, Any], asset: AssetMasterRecord, as_of: datetime) -> CanonicalMarketBar:
    price = Decimal(str(row["current_price"]))
    observed_at = as_of.astimezone(timezone.utc)
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="coingecko",
        venue=asset.venue,
        timestamp=observed_at,
        timeframe="snapshot",
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal(str(row.get("total_volume") or "0")),
        currency="USD",
        quality=RecordQuality(observed_at=observed_at, effective_at=observed_at, provider_timestamp=observed_at),
    )


def normalize_fred_observation(row: dict[str, Any], asset: AssetMasterRecord) -> CanonicalMarketBar:
    timestamp = datetime.strptime(str(row["date"]), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    value = Decimal(str(row["value"]))
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="fred",
        venue=asset.venue,
        timestamp=timestamp,
        timeframe="observation",
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("0"),
        currency="USD",
        quality=RecordQuality(effective_at=timestamp, provider_timestamp=timestamp),
    )


def normalize_treasury_rate(row: dict[str, Any], asset: AssetMasterRecord) -> CanonicalMarketBar:
    timestamp = datetime.strptime(str(row["record_date"]), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    value = Decimal(str(row["avg_interest_rate_amt"]))
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="treasury_fiscal_data",
        venue=asset.venue,
        timestamp=timestamp,
        timeframe="observation",
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("0"),
        currency="USD",
        quality=RecordQuality(effective_at=timestamp, provider_timestamp=timestamp),
    )


def normalize_coinbase_candle(row: list[Any], asset: AssetMasterRecord) -> CanonicalMarketBar:
    timestamp = datetime.fromtimestamp(int(row[0]), tz=timezone.utc)
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="coinbase_public",
        venue=asset.venue,
        timestamp=timestamp,
        timeframe="1m",
        low=Decimal(str(row[1])),
        high=Decimal(str(row[2])),
        open=Decimal(str(row[3])),
        close=Decimal(str(row[4])),
        volume=Decimal(str(row[5])),
        currency="USD",
        quality=RecordQuality(effective_at=timestamp, provider_timestamp=timestamp),
    )


def normalize_kraken_ticker(row: dict[str, Any], asset: AssetMasterRecord, as_of: datetime) -> CanonicalMarketBar:
    price = Decimal(str(row["c"][0]))
    observed_at = as_of.astimezone(timezone.utc)
    return CanonicalMarketBar(
        asset_id=asset.asset_id,
        canonical_symbol=asset.canonical_symbol,
        asset_type=asset.asset_type,
        provider="kraken_public",
        venue=asset.venue,
        timestamp=observed_at,
        timeframe="snapshot",
        open=Decimal(str(row["o"])),
        high=Decimal(str(row["h"][1])),
        low=Decimal(str(row["l"][1])),
        close=price,
        volume=Decimal(str(row["v"][1])),
        currency="USD",
        quality=RecordQuality(observed_at=observed_at, effective_at=observed_at, provider_timestamp=observed_at),
    )


def normalize_sec_submission_event(row: dict[str, Any], asset: AssetMasterRecord) -> dict[str, Any]:
    return {
        "asset_id": asset.asset_id,
        "canonical_symbol": asset.canonical_symbol,
        "provider": "sec_edgar",
        "record_type": "filing_event",
        "accession_number": row["accessionNumber"],
        "filing_date": row["filingDate"],
        "form": row["form"],
        "primary_document": row.get("primaryDocument"),
    }


def normalize_tradier_option_quote(row: dict[str, Any], asset: AssetMasterRecord) -> dict[str, Any]:
    greeks = row.get("greeks") or {}
    return {
        "asset_id": asset.asset_id,
        "provider": "tradier",
        "record_type": "option_quote",
        "symbol": row["symbol"],
        "bid": row.get("bid"),
        "ask": row.get("ask"),
        "last": row.get("last"),
        "delta": greeks.get("delta"),
        "gamma": greeks.get("gamma"),
        "theta": greeks.get("theta"),
        "vega": greeks.get("vega"),
        "iv": greeks.get("mid_iv") or greeks.get("smv_vol"),
    }


def normalize_alpaca_position(row: dict[str, Any], asset: AssetMasterRecord) -> dict[str, Any]:
    return {
        "asset_id": asset.asset_id,
        "provider": "alpaca_basic",
        "record_type": "paper_position",
        "symbol": row["symbol"],
        "qty": str(row.get("qty", "0")),
        "market_value": str(row.get("market_value", "0")),
        "unrealized_pl": str(row.get("unrealized_pl", "0")),
    }


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
