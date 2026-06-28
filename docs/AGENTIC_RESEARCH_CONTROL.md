# Agentic Research Control

QuantTools should behave like a controlled multi-agent research system, not a collection of ad hoc scripts. Each lane has a narrow responsibility, a dry-run default, and a gate before it can touch provider APIs, cloud storage, or LEAN cloud resources.

## Agents

| Agent | Responsibility | Output |
| --- | --- | --- |
| `asset-curator` | Maintains asset master, provider symbols, tags, and status | `asset_master` updates |
| `source-scout` | Reviews provider docs, rate limits, freshness, and terms | source matrix updates |
| `market-data-scout` | Plans equity/ETF/index bar acquisition | dry-run provider tasks |
| `derivatives-scout` | Plans options, greeks, 0DTE, futures, and volatility inputs | options/greeks tasks |
| `macro-rates-scout` | Plans SOFR, Fed funds, Treasury, CPI, macro releases | macro/rates tasks |
| `onchain-and-crypto-scout` | Plans crypto venues, EVM events, Bitcoin traces, DeFi context | crypto/on-chain tasks |
| `cost-sentinel` | Enforces zero-cost defaults and cloud/API call caps | cost gate decision |
| `validation-gate` | Runs Pydantic validation, quarantine, dedupe, and fixture tests | validation report |
| `lean-runner` | Runs local LEAN tests/backtests only after hypothesis approval | run ledger entries |
| `execution-policy` | Allows read-only checks, blocks cloud writes/backtests unless explicitly enabled | allow/block decision |
| `publication-reviewer` | Decides whether results are public-ready | publish/hold decision |

## Control Flow

1. `asset-curator` selects active/watchlist assets from the asset master.
2. `source-scout` ranks providers for each asset by quality, freshness, cost, and legal/terms constraints.
3. `cost-sentinel` forces `dry_run=True` unless network/cloud flags are explicitly enabled.
4. Scout agents emit provider tasks, not direct network calls.
5. Provider adapters fetch raw payloads only inside configured call/byte limits.
6. `validation-gate` converts raw payloads to canonical JSON or quarantine records.
7. Canonical records become inputs to LEAN research, paper-trading review, or portfolio calculations.
8. `lean-runner` runs local LEAN first; cloud research/backtests require explicit hypothesis and account/node readiness.
9. `publication-reviewer` blocks public claims that lack fixtures, tests, caveats, or run-ledger evidence.

## Hard Defaults

- `dry_run=True`
- `network_enabled=False`
- `cloud_writes_enabled=False`
- max provider calls per plan: `25`
- max records per run: `5000`
- max raw payload bytes per run: `5_000_000`

## LEAN Access State

LEAN CLI is installed locally at `/home/opencode/.local/bin/lean`.

Current status:

- CLI version check works.
- LEAN CLI is authenticated in this local shell.
- `lean cloud status` on checked projects reports no live deployment.
- Cloud object store root read returned no objects.
- Local backtest is currently blocked because Docker is installed but this user does not have direct Docker access without `sudo`.
- Cloud backtests remain blocked by policy until a written hypothesis and cost decision are approved.

Generate the dry-run source matrix without provider calls:

```bash
python3 -m services.orchestration.source_matrix --purpose daily_baseline
```

If authentication must be refreshed:

```bash
/home/opencode/.local/bin/lean login
```

Use a QuantConnect user ID and API token from the QuantConnect account page. Do not commit those credentials. After login, use read-only checks first:

```bash
/home/opencode/.local/bin/lean whoami
/home/opencode/.local/bin/lean cloud status <project-name>
```

Do not run `lean cloud backtest`, `lean cloud live`, or cloud object-store writes unless `execution-policy` allows the request.

## Promotion Rule

An agentic workflow is publishable only when it has:

- asset-master entries
- provider catalog entries
- dry-run task planning
- fixture payloads
- canonical validation tests
- quarantine path tests
- cost guardrails
- run-ledger evidence or explicit “not yet run” status
