# QuantTools

[![Quant Quality Gate](https://github.com/AIML-Solutions/QuantTools/actions/workflows/ci.yml/badge.svg)](https://github.com/AIML-Solutions/QuantTools/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)

**QuantTools** is AIML Solutions’ quantitative engineering lane for market data, derivatives analytics, and strategy infrastructure.

It is a portfolio-facing proof point for Python quant engineering, LEAN research workflows, options/greeks analysis, data validation, and agent-ready query surfaces.

## What this repo does

- Executes LEAN backtests and strategy research workflows
- Ingests structured market/derivatives outputs into PostgreSQL
- Exposes query surfaces through GraphQL and JSON-RPC
- Provides hooks for MCP-enabled agent tooling
- Supports options/greeks analytics and scenario research

## Current implementation highlights

- LEAN authenticated with baseline backtest validated
- Postgres + Hasura + Qdrant stack operational
- Backtest summary ingestion to Postgres verified
- GraphQL query path verified
- Market-hours and data-source mapping documented

## Key documents

- [docs/architecture.md](docs/architecture.md)
- [docs/runbook.md](docs/runbook.md)
- [docs/data-sources-and-market-hours.md](docs/data-sources-and-market-hours.md)
- [docs/DATA_PIPELINE_SPEC.md](docs/DATA_PIPELINE_SPEC.md)
- [docs/OPTIONS_GREEKS_PLAYBOOK.md](docs/OPTIONS_GREEKS_PLAYBOOK.md)
- [docs/graphql-examples.md](docs/graphql-examples.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)

## Quick start

```bash
# LEAN auth
lean login
lean whoami

# bring up infra
cd infra
cp .env.example .env
docker compose up -d

# run baseline local backtest
cd ../lean-cli
lean backtest "baseline-strategy" --no-update
```

## Directory map

- `lean-cli/` — LEAN projects + generated backtests
- `lean/` — setup + ingestion scripts
- `infra/` — compose + schema bootstrap
- `services/validation/` — Pydantic models
- `services/rpc/` — JSON-RPC scaffold
- `services/mcp/` — MCP integration notes
- `services/options-greeks/` — pricing framework notes
- `services/blockchain/` — cross-lane chain analytics bridge

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
