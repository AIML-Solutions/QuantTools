# Data Source Readiness Audit

This document translates QuantTools into a consulting-ready service: reviewing data sources before teams scale ingestion, model workflows, backtests, or agent-accessible query surfaces.

## Who It Helps

- AI teams connecting agents to public/API/paid data sources
- fintech, crypto, and market-research teams comparing providers
- analytics teams that need freshness, provenance, and ingestion-risk discipline
- startups that want a cost-aware data plan before cloud or vendor spend

## Review Areas

| Area | Output |
| --- | --- |
| Provider inventory | public/no-auth, account-required, paid, free-in-cloud, and fixture-only classification |
| Freshness | observed time, effective time, provider timestamp, and staleness expectations |
| Provenance | source, symbol, endpoint, provider, and transformation traceability |
| Smoke checks | compact public-safe readiness artifacts where terms allow |
| Source matrix | recommended provider by asset/purpose with fallback notes |
| Ingestion risk | rate limits, entitlement ambiguity, payload drift, schema gaps, and storage cost |

## Current Public Proof

- 29/29 local validation tests passing
- 4/4 public no-auth smoke checks passing at last recorded point-in-time check
- 15-row dry-run source matrix
- compact smoke example in `examples/smoke-report.example.json`
- freshness/provenance fields in canonical record quality models

## Caveats

- Smoke checks are not uptime guarantees.
- Free-in-cloud data does not imply local/bulk entitlement.
- This is data-readiness and research infrastructure work, not investment advice or live-trading evidence.
