# Project Metrics

This document records modest, reproducible metrics for QuantTools. The goal is to show engineering progress without overclaiming production scale, live trading performance, or provider availability guarantees.

## Snapshot

| Field | Value |
| --- | --- |
| Project | QuantTools |
| Snapshot date | 2026-06-30 |
| Environment | local VPS workspace |
| Cost posture | no cloud writes, no paid data download, no live/paper broker action |
| Data posture | fixtures, dry-run source matrix, and opt-in no-auth public smoke checks |
| Public-safe? | yes, with caveats |

## Verified Metrics

| Metric | Value | Evidence | Caveat |
| --- | ---: | --- | --- |
| Tests passing | 29/29 | `/home/opencode/.tmp-quanttools-validation-venv/bin/python -m unittest discover -s tests` | local venv result, not full CI matrix |
| No-auth public feed smoke checks | 4/4 OK | SEC EDGAR, Treasury Fiscal Data, Coinbase public, Kraken public | point-in-time smoke check, not uptime SLA |
| Smoke artifact size | 499 bytes | `/tmp/opencode/quanttools-network-smoke-2026-06-30.json` | summary only, no raw payload storage |
| Public smoke example | 1 | `examples/smoke-report.example.json` | compact public artifact, not raw feed data |
| Dry-run source matrix rows | 15 | `/tmp/opencode/quanttools-source-matrix-daily-2026-06-30.json` | dry-run only; no provider data pull |
| Provider catalog entries | 13 | `examples/provider_catalog.example.json` | includes providers requiring secrets/entitlements |
| Curated asset-master records | 15 | `examples/asset_master.example.json` | representative universe only |
| Public/no-auth providers represented in smoke suite | 4 | `services/ingestion/network_smoke.py` | intentionally narrow and low-cost |
| Harness/data-quality fields added | 4 | `observed_at`, `effective_at`, `provider_timestamp`, `max_staleness_seconds` | model support; downstream enforcement still expanding |
| QuantConnect dataset categories mapped | 50+ listed categories grouped | `docs/QUANTCONNECT_DATASET_MAP.md` | planning map, not entitlement proof |
| JSON-RPC candidate methods documented | 7 | `services/rpc/README.md` | scaffold/plan, not hardened service |

## Current Provider Readiness

| Provider | Current tier | Evidence | Next step |
| --- | --- | --- | --- |
| SEC EDGAR | `public_no_auth_smoke_ok` | smoke suite OK | add compact filing-event report artifact |
| Treasury Fiscal Data | `public_no_auth_smoke_ok` | smoke suite OK | add rates snapshot report artifact |
| Coinbase public | `public_no_auth_smoke_ok` | smoke suite OK | add BTC/ETH compact venue snapshot |
| Kraken public | `public_no_auth_smoke_ok` | smoke suite OK | compare with Coinbase snapshot |
| FRED | `fixture_mode` / key likely required | fixture and normalizer exist | confirm key/access before live use |
| Alpaca Basic | `requires_secret_or_account` | provider catalog and fixture style | use only with explicit paper/read-only approval |
| Tradier | `requires_secret_or_account` | option quote fixture style | use only with explicit account approval |
| QuantConnect / LEAN | authenticated CLI; cloud/free-in-cloud mapping documented | `lean whoami`, dataset map | no cloud/paid run without cost/hypothesis approval |

## Resume / Proposal Bullets

- Built a validation-first QuantTools pipeline with 29 passing local tests, 4/4 no-auth public feed smoke checks, and a 15-row dry-run source matrix across a curated ETF/equity/crypto/rates universe.
- Added provenance and freshness metadata to canonical data records, including observed time, effective time, provider timestamp, and staleness warnings.
- Mapped 50+ QuantConnect dataset categories into a cost-aware readiness model distinguishing no-auth public probes, fixtures, account-required sources, free-in-cloud data, and paid/entitlement-sensitive datasets.
- Designed JSON-RPC aggregation methods for agent-facing quant workflows while keeping cloud writes, broker actions, and bulk storage disabled by default.

## Public Caveats

- Smoke checks are point-in-time public endpoint checks, not availability or data-quality guarantees.
- Source matrix output is dry-run planning, not a provider pull.
- QuantConnect `Free in Cloud` does not imply local bulk download availability.
- No live trading, paper trading, paid cloud backtest, or paid data download is claimed by this metrics snapshot.
- This is research/data-engineering evidence, not investment advice or strategy-performance evidence.

## Next Metrics To Add

1. Compact smoke-report generator that writes timestamped summaries without raw payloads.
2. Provider readiness score combining catalog tier, fixture coverage, smoke status, and secret/entitlement requirements.
3. JSON-RPC `providers.smoke_status` and `source_matrix.daily` local methods backed by compact artifacts.
4. CI-visible test metrics once dependency specification is formalized.
5. A small `smoke-report.example.json` artifact for public demos.
