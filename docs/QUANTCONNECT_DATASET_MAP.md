# QuantConnect Dataset Map

This document summarizes the QuantConnect dataset universe relevant to QuantTools. It is a planning map, not proof that all datasets are locally available. Many QuantConnect datasets are marked `Free in Cloud`, which means they are useful for cloud research/backtests but should not be assumed available for local download or bulk export without checking account entitlements and cost.

## Operating Rules

- Do not run paid cloud backtests or paid data downloads without explicit approval.
- Treat `Free in Cloud` as cloud-entitled research data, not automatically local VPS data.
- Prefer small, curated probes and metadata checks over bulk downloads.
- Keep local artifacts compact: source matrix rows, smoke summaries, and representative fixtures.
- Use broker or paper-trading APIs only with explicit credentials/approval and never for live execution by default.

## High-Value Free / Free-In-Cloud Categories

| Category | Examples | QuantTools use |
| --- | --- | --- |
| US equity reference and prices | US Equity Security Master, US Equity Coarse Universe, US Equities | asset master, backtest universe, corporate-action context |
| US ETFs and constituents | US ETF Constituents, ETF listings | ETF sleeve research, constituents, sector/portfolio context |
| Fundamentals and filings | US Fundamental Data, US SEC Filings | quality/value screens, filing-aware research, public-company context |
| Options and derivatives | US Equity Option Universe, US Equity Options, US Index Options, US Futures, Future Options | greeks, 0DTE research, volatility, hedging, derivatives tests |
| Events | Upcoming Earnings, IPOs, Splits, Dividends, Economic Events | event calendar, strategy blackout/alert rules, macro context |
| Macro and rates | FRED, Treasury Yield Curve, EIA, BLS, macro indicators | rate-aware derivatives inputs, macro regimes, inflation/energy context |
| Crypto | Coinbase, Kraken, Binance, Bitfinex, Binance US, Bybit futures, crypto market cap, Bitcoin metadata | crypto venue comparison, volatility/liquidity, public-ledger adjacent research |
| FX/CFD/indices | Forex, CFD, Cash Indices, VIX Central Contango, Fear and Greed | cross-asset context, regime features, index/volatility research |
| News/attention | Tiingo News, Fear and Greed, Wikipedia Page Views (paid) | sentiment/attention experiments with clear entitlement boundaries |

## Paid / Entitlement-Sensitive Categories

| Category | Examples | Rule |
| --- | --- | --- |
| Premium news/sentiment | Benzinga, Brain Sentiment, Brain ML Stock Ranking, Brain Language Metrics | do not assume access; use only with approved subscription |
| Political/alternative data | Congress Trading, Corporate Lobbying, Government Contracts, Insider Trading, CNBC Trading | useful research lane, but paid/entitlement-sensitive |
| Proprietary factors | Composite Factor Bundle, Estimize, True Beats, Tactical, Cross Asset Model | paid; do not represent as implemented without entitlement |
| Regulatory alerts | RegAlytics financial-sector alerts | paid; suitable for future compliance/intelligence lane only |

## Near-Term Curated Asset Universe

Use a small universe before expanding:

| Asset | Reason | Primary free/public source | QuantConnect lane |
| --- | --- | --- | --- |
| SPY | broad US equity/ETF baseline | Stooq, SEC, QC US Equities/ETF | equity/ETF/option universe |
| QQQ | growth/tech ETF baseline | Stooq, SEC, QC US Equities/ETF | equity/ETF/option universe |
| IWM | small-cap ETF baseline | Stooq, SEC, QC US Equities/ETF | equity/ETF/option universe |
| AAPL | liquid single-name equity | SEC EDGAR, Stooq, QC equities/options | filings, options, fundamentals |
| MSFT | liquid single-name equity | SEC EDGAR, Stooq, QC equities/options | filings, options, fundamentals |
| NVDA | high-volatility AI/semiconductor equity | SEC EDGAR, Stooq, QC equities/options | volatility, event, options |
| BTC-USD | crypto benchmark | Coinbase, Kraken, CoinGecko, QC crypto | venue comparison, volatility |
| ETH-USD | crypto benchmark | Coinbase/Kraken/CoinGecko, QC crypto | venue comparison, on-chain adjacent |
| SOFR / DGS10 | rates context | FRED/Treasury | macro/rates |
| VIX / SPX / NDX | index and volatility context | QC cash/index options, public references | index options, vol regime |

## Readiness Tiers

| Tier | Meaning | Current examples |
| --- | --- | --- |
| `public_no_auth_smoke_ok` | no-auth endpoint responds to compact probe | SEC EDGAR, Treasury Fiscal Data, Coinbase public, Kraken public |
| `fixture_mode` | sample payload exists and normalizer/test covers it | SEC, Treasury, FRED fixture, Coinbase, Kraken, Tradier, Alpaca-style |
| `requires_secret_or_account` | credentials/account needed; no public probe by default | FRED API key, Alpaca, Tradier, LEAN authenticated data |
| `free_in_cloud_only` | QuantConnect lists free cloud access; local availability not assumed | US Equities, options universes, futures, fundamentals, events, crypto datasets |
| `paid_or_entitled` | subscription or explicit approval required | Benzinga, Brain, Estimize, political/alternative datasets |

## Next Implementation Targets

1. Add a compact smoke-report artifact generator that records provider, bytes, status, timestamp, and no raw payload.
2. Add provider readiness scoring from catalog + smoke result + fixture coverage.
3. Extend JSON-RPC methods to expose `source_matrix.daily`, `providers.smoke_status`, and `assets.watchlist` locally.
4. Add explicit `quantconnect_dataset_map` entries to the provider catalog without triggering downloads.
5. Only then consider a controlled cloud LEAN run with cost/hypothesis approval.
