# QuantTools

[![Quant Quality Gate](https://github.com/AIML-Solutions/QuantTools/actions/workflows/ci.yml/badge.svg)](https://github.com/AIML-Solutions/QuantTools/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)

**QuantTools** is AIML Solutions’ quantitative engineering lane for multisource asset data, derivatives analytics, portfolio research, and strategy infrastructure.

It is a portfolio-facing proof point for Python quant engineering, LEAN research workflows, options/greeks analysis, Pydantic data validation, canonical JSON normalization, and agent-ready query surfaces.

## What this repo does

- Executes LEAN backtests and strategy research workflows
- Ingests multisource market, derivatives, macro, broker, and on-chain records into normalized JSON and PostgreSQL
- Validates provider payloads with Pydantic before downstream analysis
- Maintains an asset-master approach for targeted equities, ETFs, crypto assets, crypto-linked ETFs, options, futures, and rates references
- Exposes query surfaces through GraphQL and JSON-RPC
- Provides hooks for MCP-enabled agent tooling
- Supports options/greeks analytics, portfolio calculations, paper-trading ledgers, and scenario research

## Current implementation highlights

- LEAN authenticated with baseline backtest validated
- Postgres + Hasura + Qdrant stack operational
- Backtest summary ingestion to Postgres verified
- GraphQL query path verified
- Market-hours and data-source mapping documented

## Implementation status

| Area | Status | Notes |
| --- | --- | --- |
| LEAN research workflows | Active | Multiple strategy workspaces and backtest artifacts are included under `lean-cli/` |
| Market data ingestion | Active | Broker, macro, crypto, equities, options, and on-chain ingestion paths are organized under `services/ingestion/` and `services/blockchain/` |
| Validation models | Active | Pydantic validation paths exist under `services/validation/` and `services/ingestion/` |
| Query surfaces | Scaffold/active | JSON-RPC and GraphQL-facing examples exist; production hardening remains a next step |
| Options/greeks | Scaffold/active | Framework notes and VIX/options research paths exist; expand with tested calculators and examples next |
| Asset master | Planned/active | A canonical target-universe model is being formalized for provider mappings, asset tags, and portfolio research |
| On-chain analytics | Scaffold/active | Bitcoin/Ethereum/EVM tracing and Solidity review tools are organized under `services/blockchain/` |
| Public dashboard | Active | GitHub Pages frontend artifacts summarize selected quant research outputs |

This repository is the strongest current technical proof point in the AIML Solutions portfolio. The next quality step is adding tests and a reproducible validated-demo document that ties commands to output artifacts.

## Key documents

- [docs/architecture.md](docs/architecture.md)
- [docs/runbook.md](docs/runbook.md)
- [docs/data-sources-and-market-hours.md](docs/data-sources-and-market-hours.md)
- [docs/MULTISOURCE_ASSET_PIPELINE.md](docs/MULTISOURCE_ASSET_PIPELINE.md)
- [docs/AGENTIC_RESEARCH_CONTROL.md](docs/AGENTIC_RESEARCH_CONTROL.md)
- [docs/SOURCE_SELECTION_STRATEGY.md](docs/SOURCE_SELECTION_STRATEGY.md)
- [docs/PRODUCTION_QUALITY_GATE.md](docs/PRODUCTION_QUALITY_GATE.md)
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

Generate a dry-run source matrix without touching provider APIs:

```bash
python3 -m services.orchestration.source_matrix --purpose daily_baseline
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
