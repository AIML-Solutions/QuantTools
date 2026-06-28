# Data Pipeline Spec (Quant Lane)

## Goal
Provide reliable, replayable, and analyzable market data pipelines for MultiClaw research, portfolio analysis, paper-trading review, and strategy operations.

QuantTools uses a targeted asset-master approach: select a bounded universe, map each asset across providers, normalize records into canonical JSON, validate with Pydantic, then store and expose clean records for research.

## Stages
1. **Source acquisition** (LEAN/local/provider-based)
2. **Normalization** (symbol/timezone/session coherence)
3. **Validation** (schema and value constraints)
4. **Canonical JSON emission** (provider-attributed records)
5. **Storage** (Postgres canonical tables and fixture artifacts)
6. **Access** (GraphQL + JSON-RPC)
7. **Monitoring** (lag, gaps, anomalies)

## Canonical entities
- `reference.asset_master`
- `market.bars`
- `options.greeks_snapshot`
- `portfolio.paper_ledger`
- `onchain.transaction_event`
- `backtests.run_summary`

## Required quality checks
- timestamp monotonicity within symbol stream
- no duplicate natural keys
- data type and range validation
- session-window compliance using market-hours metadata

## Failure handling
- write failed records to quarantine log
- emit structured error context
- allow idempotent reprocessing
