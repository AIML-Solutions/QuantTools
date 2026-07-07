# JSON-RPC Layer (Planned)

Purpose: expose deterministic quant operations for OpenClaw/MCP without overloading GraphQL.

## Candidate Methods
- `backtest.run(project, start, end, params)`
- `backtest.status(run_id)`
- `market.bars(symbol, resolution, from, to)`
- `options.greeks(symbol, ts, model)`
- `source_matrix.daily(purpose, caps)`
- `providers.smoke_status()`
- `assets.watchlist()`
- `signals.latest(strategy)`

## Recommended Stack
- FastAPI transport + JSON-RPC 2.0 method handlers
- Pydantic request/response schemas
- Auth via local token or mTLS on private network

## Why both GraphQL and JSON-RPC?
- GraphQL: flexible read/query layer (dashboards + analysts)
- JSON-RPC: strict command/action interface (agents + automation)

## Local-First Aggregation Plan

The JSON-RPC layer should start as a local harness around compact artifacts, not as a cloud service.

Near-term methods:

| Method | Backing artifact | Purpose |
| --- | --- | --- |
| `system.ping` | runtime clock | health check |
| `source_matrix.daily` | `services.orchestration.source_matrix` dry-run output | explain selected providers without touching APIs |
| `providers.smoke_status` | opt-in `network_smoke` summary | report which no-auth feeds responded |
| `assets.watchlist` | `examples/asset_master.example.json` | expose curated assets for agents/dashboards |
| `options.greeks` | placeholder until calculator is wired | keep method contract stable |

Guardrails:

- Do not store raw bulk provider payloads by default.
- Do not perform cloud writes from RPC methods unless `ENABLE_CLOUD_WRITES=1` and explicit approval are present.
- Do not perform broker, paper-trading, or live-trading actions from this scaffold.
- Keep free/no-auth network probes opt-in with `ENABLE_NETWORK_TESTS=1`.
