from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


AssetType = Literal["equity", "etf", "option", "future", "crypto", "token", "index", "rate", "macro"]
AssetStatus = Literal["candidate", "active", "watchlist", "paused", "retired"]


class MarketBar(BaseModel):
    symbol: str = Field(min_length=1)
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Decimal("0")
    source: str = "lean"


class AssetMasterRecord(BaseModel):
    asset_id: str = Field(min_length=3)
    asset_type: AssetType
    canonical_symbol: str = Field(min_length=1)
    provider_symbols: dict[str, str] = Field(default_factory=dict)
    venue: str = Field(min_length=1)
    timezone: str = "UTC"
    session_rules: str = "provider_default"
    research_tags: list[str] = Field(default_factory=list)
    data_priority: str = "standard"
    status: AssetStatus = "candidate"

    @field_validator("asset_id")
    @classmethod
    def asset_id_must_include_namespace(cls, value: str) -> str:
        if ":" not in value:
            raise ValueError("asset_id must include a namespace, for example equity:usa:SPY")
        return value


class RecordQuality(BaseModel):
    schema_version: str = "0.1.0"
    validated: bool = True
    source_latency_ms: int | None = Field(default=None, ge=0)
    warnings: list[str] = Field(default_factory=list)


class CanonicalMarketBar(BaseModel):
    asset_id: str = Field(min_length=3)
    canonical_symbol: str = Field(min_length=1)
    asset_type: Literal["equity", "etf", "crypto", "token", "index", "rate", "macro"]
    provider: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    timestamp: datetime
    timeframe: str = Field(min_length=1)
    open: Decimal = Field(ge=0)
    high: Decimal = Field(ge=0)
    low: Decimal = Field(ge=0)
    close: Decimal = Field(ge=0)
    volume: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = "USD"
    quality: RecordQuality = Field(default_factory=RecordQuality)

    @model_validator(mode="after")
    def validate_bar_ranges(self):
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if not (self.low <= self.open <= self.high):
            raise ValueError("open must be between low and high")
        if not (self.low <= self.close <= self.high):
            raise ValueError("close must be between low and high")
        return self


class CanonicalOptionSnapshot(BaseModel):
    asset_id: str = Field(min_length=3)
    underlying_asset_id: str = Field(min_length=3)
    canonical_symbol: str = Field(min_length=1)
    asset_type: Literal["option"] = "option"
    timestamp: datetime
    expiry: str = Field(min_length=8)
    strike: Decimal = Field(gt=0)
    right: Literal["call", "put"]
    implied_volatility: Decimal | None = Field(default=None, ge=0)
    delta: Decimal | None = Field(default=None, ge=Decimal("-1"), le=Decimal("1"))
    gamma: Decimal | None = Field(default=None, ge=0)
    theta: Decimal | None = None
    vega: Decimal | None = Field(default=None, ge=0)
    open_interest: Decimal | None = Field(default=None, ge=0)
    quality: RecordQuality = Field(default_factory=RecordQuality)


class OnChainTransactionEvent(BaseModel):
    asset_id: str = Field(min_length=3)
    chain: Literal["bitcoin", "ethereum", "evm"]
    provider: str = Field(min_length=1)
    timestamp: datetime
    tx_hash: str = Field(min_length=10)
    event_type: str = Field(min_length=1)
    from_address: str | None = None
    to_address: str | None = None
    value: Decimal | None = Field(default=None, ge=0)
    contract_address: str | None = None
    quality: RecordQuality = Field(default_factory=RecordQuality)


class GreeksSnapshot(BaseModel):
    underlying: str
    option_symbol: str
    ts: datetime
    price: Decimal
    iv: Decimal | None = None
    delta: Decimal | None = None
    gamma: Decimal | None = None
    vega: Decimal | None = None
    theta: Decimal | None = None
    rho: Decimal | None = None
    model: str = "unspecified"
