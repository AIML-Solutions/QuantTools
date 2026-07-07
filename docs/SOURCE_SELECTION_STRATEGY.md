# Source Selection Strategy

This document defines how QuantTools should decide what data it can pull, what data it should pull, and how to stay inside a near-zero-cost operating envelope while still demonstrating production-level quant data engineering.

The core idea is selective aggregation: maintain a small asset master, map each asset to multiple possible providers, choose the best source per use case, and avoid duplicate storage or uncontrolled polling.

See also [`QUANTCONNECT_DATASET_MAP.md`](QUANTCONNECT_DATASET_MAP.md) for a curated map of QuantConnect free, free-in-cloud, and paid/entitlement-sensitive datasets.

## Operating Constraints

- Use paid subscriptions only where already intentionally authorized, such as a QuantConnect research subscription.
- Keep public repos free of API keys, account IDs, tokens, live broker details, and provider entitlements.
- Prefer read-only, paper-trading, delayed, daily, or fixture-based workflows before real-time polling.
- Keep cloud spend effectively zero by default, with budgets, object lifecycle rules, storage caps, and local-first processing.
- Treat provider terms, exchange data policies, and redistribution limits as design constraints.
- Store raw payloads only when needed for replay/debugging; store canonical records as the primary analysis substrate.

## Source Universe

| Source | Candidate use | Freshness | Cost posture | Quality posture | Initial role |
| --- | --- | --- | --- | --- | --- |
| QuantConnect / LEAN | Historical equities, options universes, futures, forex, crypto, backtests, market-hours metadata | Historical/backtest; cloud/live depends on account/node | Subscription-backed; avoid accidental cloud-node usage | Strong for research because data is integrated, vetted, and backtest-ready | Primary research/backtest source |
| Alpaca Basic | Paper account state, equities IEX feed, crypto, limited options data | IEX real-time for equities; other free-plan limits; historical restrictions | Free Basic, rate-limited | Good for paper-first execution review, not full-market US equity tape | Paper execution + IEX comparison feed |
| Tradier | Quotes, option chains/greeks, paper/live brokerage context | API quote freshness depends plan/session | Free/account-based access; must respect rate limits | Useful for options/greeks comparison and chain metadata | Options chain/greeks candidate |
| Charles Schwab / thinkorswim | Account/brokerage data if approved | Depends API access | Account/API approval required | Useful if accessible; do not assume availability | Candidate broker lane |
| Public.com | Account/API data if API access is available | Unknown until docs/key tested | Candidate free/account API | Requires API documentation and test fixture before use | Hold for verification |
| Stooq | Daily equity/ETF historical bars | Daily/EOD | Free public source | Useful EOD fallback; not real-time | Baseline daily fallback |
| FRED | Rates, SOFR, Fed funds, CPI, unemployment, macro series | Release schedule / daily where applicable | Free API key | Authoritative macro/rates source | Primary macro/rates source |
| Treasury Fiscal Data | Treasury rates, debt, fiscal finance, exchange rates | Dataset-specific; API is open | Free/no token | Authoritative federal finance data | Treasury/rates/fiscal source |
| SEC EDGAR APIs | Filings, submissions, XBRL company facts | Near-real-time filings; nightly bulk ZIPs | Free/no auth | Authoritative fundamentals/filings source | Fundamentals/event context |
| Alpha Vantage | Daily/weekly/monthly equities, FX, commodities, indicators, some options | Free endpoints limited; premium for stronger intraday/realtime | Free key but throttled; many endpoints premium | Useful breadth, but must detect rate limits and entitlement messages | Secondary/fallback source |
| CoinGecko | Crypto market data, categories, coins, DEX/on-chain via related products | Demo/free limited; paid for larger scale | Free/demo tier possible | Broad crypto coverage; provider attribution required | Crypto universe/reference source |
| Coinbase Exchange public API | Crypto ticker/candles/order-book-style market data | Public ticker; candles with 300 max points/request | Public unauthenticated endpoints for some market data | Good BTC/ETH/USD venue source; avoid frequent polling | Crypto venue feed |
| Kraken public API | Crypto ticker/market data | Public ticker | Public unauthenticated endpoint | Good cross-venue crypto comparison | Crypto venue feed |
| Etherscan API V2 | Ethereum and EVM token transfers, balances, names, contract/tx data | API-dependent; multi-chain via `chainid` | Free tiers exist; key required | Good EVM explorer source; not a substitute for archive node traces | EVM event/enrichment source |
| DefiLlama | TVL, DEX/perp/options volume, stablecoins, yields, protocol metrics | API/dashboard dependent | Free public ecosystem data | Useful DeFi macro context; avoid double-counting | DeFi context source |
| Direct public RPC | Bitcoin/Ethereum/EVM reads, receipts/logs if supported | Node/provider dependent | Free public endpoints are limited | Useful for demos; unreliable for heavy tracing | Fixture/demo only until provider chosen |

## Source Priority By Asset Class

| Asset class | Preferred source | Secondary source | Avoid by default |
| --- | --- | --- | --- |
| US equities / ETFs, daily | QuantConnect/LEAN, Stooq | Alpha Vantage compact daily | High-frequency polling across broad lists |
| US equities / ETFs, intraday | QuantConnect where entitled, Alpaca IEX for free real-time sample | Alpha Vantage if entitlement allows | Assuming IEX equals full market tape |
| US options / greeks | QuantConnect options universes, Tradier greeks | Alpaca indicative/options where available | OPRA-like claims without paid entitlement |
| Futures / futures options | QuantConnect/LEAN | none until verified | Free web scraping |
| Rates / SOFR / macro | FRED | Treasury Fiscal Data | Vendor indicators without provenance |
| Fundamentals / filings | SEC EDGAR APIs | Alpha Vantage company overview as secondary | Treating scraped summaries as canonical |
| Crypto spot | Coinbase, Kraken, CoinGecko | LEAN crypto data | Storing high-frequency ticks for broad universe |
| Crypto ETFs | Equity/ETF lane plus crypto context lane | SEC filings for product context | Blending ETF and spot crypto without asset IDs |
| On-chain EVM | Etherscan, public RPC fixtures | DefiLlama protocol context | Deep traces on free public RPC as a production assumption |
| Bitcoin ledger | Public APIs/fixtures first; later selected node/provider | CoinGecko/Coinbase/Kraken market context | Heavy recursive tracing without cost model |

## Decision Rules

1. Start from `asset_master.example.json`, not from provider availability.
2. For each asset, define the research question before pulling data.
3. Choose the lowest-cost source that is good enough for that question.
4. Prefer daily/EOD and backtest data for broad coverage.
5. Use near-real-time feeds only for narrow watchlists and paper-trading diagnostics.
6. Store canonical JSON with provider attribution, not provider-native blobs as the main record.
7. Deduplicate by natural key: asset ID, timestamp, timeframe, provider, and record type.
8. Quarantine invalid records instead of silently dropping or force-casting them.
9. Promote a provider only after fixture tests, live smoke tests, and rate-limit behavior are documented.

## Asset Master Expansion Plan

The initial master list should be deliberately small:

| Sleeve | Example assets | Purpose |
| --- | --- | --- |
| Broad-market ETFs | SPY, QQQ, IWM | Market beta, options, 0DTE experiments |
| Volatility/rates context | VIX-related proxies, SOFR/Fed funds/Treasury rates | Derivatives and scenario analysis |
| Mega-cap/liquidity names | AAPL, MSFT, NVDA, TSLA | Liquid options and event/fundamental context |
| Crypto majors | BTC-USD, ETH-USD | Crypto spot, ETF correlation, on-chain context |
| Crypto-linked equities/ETFs | BITO, IBIT-like products if selected | Bridge traditional market and crypto exposure |
| Defensive/risk assets | GLD, TLT, UUP-like candidates | Stress/regime research |

Each asset should include provider symbol mappings, session rules, asset type, tags, and minimum cadence.

## Free-Tier Cloud Guardrails

The safest production-style design is local-first, object-storage-light, and budget-enforced.

### AWS

- Use S3 only for compressed canonical fixtures, small parquet/jsonl partitions, and reports.
- Enable billing alerts and a hard budget alert before using any service.
- Block public access by default.
- Add lifecycle rules to expire raw payloads quickly.
- Do not run always-on compute for ingestion.
- Prefer local cron/manual jobs until an event-driven free-tier workflow is proven.

### Google Cloud

- Candidate free-tier services: Cloud Storage, BigQuery free monthly query allowance, Cloud Run, Pub/Sub, Secret Manager, Cloud Shell.
- Keep BigQuery datasets small and partitioned if used.
- Treat BigQuery as optional analytics, not the primary store, until cost monitoring is proven.

### Azure

- Candidate free-tier services: Blob Storage, Functions, Static Web Apps, Cosmos DB free tier, Azure SQL free tier, Key Vault free transactions.
- Prefer Blob Storage for static artifacts and Functions only for small scheduled demos.
- Avoid paid networking, managed databases, and always-on compute by default.

### Universal zero-cost rules

- Default mode is `DRY_RUN=1`.
- Network tests require explicit `ENABLE_NETWORK_TESTS=1`.
- Cloud writes require explicit `ENABLE_CLOUD_WRITES=1`.
- Max raw payload size per run should be configured.
- Max rows per provider per run should be configured.
- Every cloud bucket/container path should include lifecycle expiration for raw data.
- Dashboards should read from static generated artifacts where possible.

## Researcher Seat / LEAN Usage Plan

The LEAN lane should be treated as a scarce, valuable research environment.

- Verify CLI installation and authentication before running cloud workflows.
- Record `lean whoami` and organization/workspace status locally, not in public docs if it exposes account details.
- Use local backtests for first-pass strategy iteration.
- Use cloud backtests/research nodes only for selected strategy runs with a written hypothesis.
- Export backtest summaries, orders, statistics, and charts into sanitized artifacts.
- Track each run in a run ledger with data source, date range, strategy version, parameters, and cost posture.
- Never present backtest results without caveats on slippage, fees, data quality, overfitting, and out-of-sample validation.

Current local state: LEAN CLI is installed at `/home/opencode/.local/bin/lean` and authenticated in this shell. Read-only checks work. Local Docker backtests are blocked until Docker can run without a privileged prompt, and cloud backtests remain blocked until an explicit hypothesis/cost decision is approved.

## What To Build Next Before Publishing More

1. Add source-ranking metadata to each asset: preferred, fallback, prohibited.
2. Add an opt-in network smoke-test suite that skips unless environment variables are present.
3. Add a local report generator that writes source-quality matrix artifacts for dashboard use.
4. Add provider-specific rate-limit documentation once real account plans are confirmed.
5. Add Docker/LEAN local-backtest readiness checks that do not require privileged prompts.
