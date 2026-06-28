# Multisource Asset Pipeline

QuantTools is evolving into a targeted asset-intelligence pipeline: gather data from multiple accessible providers, validate and normalize it, then use the resulting records for portfolio research, derivatives analysis, and strategy evaluation.

The emphasis is not on claiming alpha. The emphasis is on building the data discipline required before any strategy can be trusted.

## Product thesis

Most useful quant systems need a consistent view of a narrow asset universe before they need more indicators. QuantTools treats each selected asset as a research object with repeatable data intake, schema validation, provenance, and downstream analysis hooks.

The pipeline is designed for:

- equities, ETFs, crypto assets, crypto-linked ETFs, indexes, options, futures, and macro/rate references
- derivatives research including options chains, greeks, volatility, expiry structure, and 0DTE-specific experiments
- portfolio-level calculations such as exposures, sleeves, drawdown behavior, and scenario analysis
- on-chain feature extraction for Bitcoin, Ethereum, EVM chains, tokens, and smart-contract risk signals
- paper-trading and backtest feedback loops before any real execution workflow is considered

## Asset master

The asset master is the control surface for the system. It defines what assets are worth tracking and how they should be mapped across providers.

Planned fields include:

| Field | Purpose |
| --- | --- |
| `asset_id` | Internal stable identifier |
| `asset_type` | Equity, ETF, option, future, crypto, token, index, rate, or macro series |
| `canonical_symbol` | Normalized symbol used inside QuantTools |
| `provider_symbols` | Provider-specific mappings and aliases |
| `venue` | Exchange, broker, chain, or data venue |
| `timezone` | Canonical market or chain timestamp context |
| `session_rules` | Market-hours or 24/7 handling rules |
| `research_tags` | Strategy, sector, theme, risk, or portfolio sleeve tags |
| `data_priority` | Minimum required cadence and acceptable provider fallback |
| `status` | Candidate, active, watchlist, paused, or retired |

The master list should stay small enough to inspect manually and broad enough to support cross-asset research.

## Source categories

QuantTools is designed to combine provider categories rather than depend on a single feed.

| Category | Examples of use | Notes |
| --- | --- | --- |
| LEAN / QuantConnect research data | Backtests, market-hours metadata, historical bars, options universes | Primary research and validation lane where available |
| Broker and paper-trading APIs | Portfolio snapshots, order-state experiments, paper execution telemetry | Read-only or paper-first workflows only |
| Free market-data APIs | Quotes, reference metadata, macro/rate series, crypto market data | Must be rate-limited, cached, and provider-attributed |
| Exchange and crypto APIs | Spot/derivatives data, funding, open interest, volume, order-book samples | Narrow scope first because cost/storage can expand quickly |
| On-chain RPC and explorers | Transaction receipts, logs, token transfers, contract metadata | Start with read-only tracing and event extraction |
| Research feeds | ArXiv/SSRN/news or filings-derived signals | Used for strategy backlog and hypothesis tracking, not direct trading signals |

API keys, account identifiers, and provider entitlements must not be committed. Public examples should use mock records, documented schemas, and reproducible local samples.

## Pipeline stages

1. **Select assets** from the asset master.
2. **Acquire data** from source adapters with rate limits, retry policy, and provider attribution.
3. **Normalize records** into canonical JSON shapes with unified symbols, timestamps, units, and venues.
4. **Validate records** with Pydantic models and explicit range/type/session checks.
5. **Quarantine failures** with structured error context for replay.
6. **Store canonical records** in Postgres and file artifacts where useful.
7. **Expose query surfaces** through GraphQL, JSON-RPC, and agent-facing tools.
8. **Analyze portfolios and strategies** with backtests, paper-trade ledgers, options scenarios, and cross-asset reports.

## Canonical JSON shape

Representative market-bar record:

```json
{
  "asset_id": "equity:usa:SPY",
  "canonical_symbol": "SPY",
  "asset_type": "etf",
  "provider": "example_provider",
  "venue": "usa_equity",
  "timestamp": "2026-06-28T14:30:00Z",
  "timeframe": "1m",
  "open": 0.0,
  "high": 0.0,
  "low": 0.0,
  "close": 0.0,
  "volume": 0,
  "currency": "USD",
  "quality": {
    "schema_version": "0.1.0",
    "validated": true,
    "source_latency_ms": null,
    "warnings": []
  }
}
```

Representative option snapshot:

```json
{
  "asset_id": "option:usa:SPY:2026-06-30:CALL:600",
  "underlying_asset_id": "equity:usa:SPY",
  "canonical_symbol": "SPY 2026-06-30 600C",
  "asset_type": "option",
  "timestamp": "2026-06-28T14:30:00Z",
  "expiry": "2026-06-30",
  "strike": 600.0,
  "right": "call",
  "implied_volatility": null,
  "delta": null,
  "gamma": null,
  "theta": null,
  "vega": null,
  "open_interest": null,
  "quality": {
    "schema_version": "0.1.0",
    "validated": true,
    "warnings": []
  }
}
```

## Validation principles

- Reject records with missing canonical asset IDs.
- Normalize timestamps to UTC while retaining session context.
- Keep provider attribution on every ingested record.
- Validate symbol mappings before writing market data.
- Check ranges for prices, volume, greeks, rates, and volatility.
- Detect duplicate natural keys before storage.
- Separate raw provider payloads from canonical records.
- Quarantine invalid records rather than silently dropping them.

## Strategy and portfolio use cases

QuantTools is meant to support research workflows such as:

- LEAN backtests and walk-forward validation
- sleeve allocation and portfolio risk decomposition
- options/greeks dashboards for covered calls, spreads, volatility, and 0DTE experiments
- SOFR/rate-aware scenario inputs for derivatives and portfolio stress tests
- crypto spot/ETF correlation and volatility studies
- on-chain event features for token, wallet, and protocol risk monitoring
- paper-trading ledgers that compare hypothesis, signal, order, fill, and realized outcome

All public strategy examples should include caveats, transaction-cost assumptions, and out-of-sample validation notes.

## On-chain extension

The blockchain lane extends the same data discipline to crypto ledgers and smart contracts:

- Bitcoin UTXO transaction tracing
- Ethereum/EVM receipt and log decoding
- ERC-20 and DEX transfer-flow extraction
- Solidity static checks and OpenZeppelin-pattern review
- contract-event features that can be joined to price, liquidity, and volatility records

Deep traces may require archive nodes or provider support. Public tooling should degrade gracefully when a free RPC endpoint does not expose debug methods.

## Near-term deliverables

- Create `asset_master.example.json` with a small representative universe.
- Add Pydantic models for asset metadata, market bars, option snapshots, and on-chain events.
- Add fixtures for provider-normalized records.
- Add tests for symbol mapping, timestamp normalization, validation failures, and quarantine records.
- Add a reproducible demo that ingests fixtures and emits canonical JSON.
