# Production Quality Gate

QuantTools should not publish a provider, strategy, or portfolio-analysis lane as production-ready until it passes these gates. Public artifacts may show architecture, fixtures, and dry-run validation earlier, but they must label incomplete paths honestly.

## Data-source gate

- Provider credentials are loaded only from environment variables or local secret stores.
- No API keys, account IDs, tokens, or provider entitlement details are committed.
- Raw provider payloads are preserved only as local artifacts or safe public fixtures.
- Every provider record includes source attribution and retrieval timestamp.
- Rate limits, retry behavior, and failure modes are documented per provider.

## Normalization gate

- Each target asset maps through `AssetMasterRecord` before ingestion.
- Canonical records use stable `asset_id` values rather than provider-only symbols.
- Timestamps normalize to UTC while preserving market/session context.
- Market bars, option snapshots, paper-trading records, and on-chain events have Pydantic validation.
- Invalid records create `QuarantineRecord` objects with reason, source, payload, and run ID.
- Natural keys are explicit and duplicate handling is deterministic.

## Research gate

- Strategy examples include transaction-cost, slippage, and data-quality caveats.
- Backtests include out-of-sample or walk-forward notes before they are highlighted.
- Paper-trading outputs are separated from live execution claims.
- Portfolio calculations show assumptions for rates, fees, margin, and instrument type.
- Options/0DTE experiments document expiry handling, greeks source, and assignment risk assumptions.

## On-chain gate

- Chain analysis is read-only by default.
- Public RPC limitations are treated as expected behavior, not silent failures.
- Smart-contract scans are labeled static-analysis support, not audits.
- Solidity/OpenZeppelin checks include rule descriptions and false-positive caveats.
- Address, wallet, and transaction examples are public-chain or synthetic fixtures.

## Test gate

- Fixture validation tests pass without real credentials.
- Normalization tests cover valid, invalid, duplicate, and quarantine paths.
- Provider adapters have dry-run tests before network tests.
- Network tests are opt-in and skipped unless explicit environment variables are present.
- LEAN cloud backtests are opt-in and require an approved hypothesis, expected cost posture, and run-ledger entry.
- Local LEAN backtests require Docker access without privileged prompts.
- `git diff --check` passes before commit.

## Publication rule

Publish only what can be demonstrated with safe fixtures, local validation, or documented commands. Keep live credentials, active account screenshots, and provider-specific entitlements out of public repos.
