from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from typing import Any
from urllib import parse, request


ENABLE_NETWORK_ENV = "ENABLE_NETWORK_TESTS"


@dataclass(frozen=True)
class SmokeRequest:
    provider: str
    url: str
    expected_keys: tuple[str, ...]
    timeout_seconds: int = 10
    max_bytes: int = 500_000


@dataclass(frozen=True)
class SmokeResult:
    provider: str
    skipped: bool
    ok: bool
    reason: str
    bytes_read: int = 0


def network_enabled(env: dict[str, str] | None = None) -> bool:
    values = env if env is not None else os.environ
    return values.get(ENABLE_NETWORK_ENV) == "1"


def default_smoke_requests() -> list[SmokeRequest]:
    sec_url = "https://data.sec.gov/submissions/CIK0000320193.json"
    treasury_url = (
        "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
        "v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&page[size]=1&sort=-record_date"
    )
    coinbase_url = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
    kraken_url = "https://api.kraken.com/0/public/Ticker?" + parse.urlencode({"pair": "XBTUSD"})
    return [
        SmokeRequest("sec_edgar", sec_url, ("cik", "filings")),
        SmokeRequest("treasury_fiscal_data", treasury_url, ("data", "meta")),
        SmokeRequest("coinbase_public", coinbase_url, ("price", "time")),
        SmokeRequest("kraken_public", kraken_url, ("result", "error")),
    ]


def run_smoke_request(smoke: SmokeRequest, enabled: bool | None = None) -> SmokeResult:
    if enabled is None:
        enabled = network_enabled()
    if not enabled:
        return SmokeResult(smoke.provider, skipped=True, ok=False, reason=f"set {ENABLE_NETWORK_ENV}=1 to run")

    req = request.Request(smoke.url, headers={"User-Agent": "AIML-Solutions-QuantTools/0.1 smoke-test"})
    with request.urlopen(req, timeout=smoke.timeout_seconds) as response:
        payload = response.read(smoke.max_bytes + 1)
    if len(payload) > smoke.max_bytes:
        return SmokeResult(smoke.provider, skipped=False, ok=False, reason="response exceeded max_bytes", bytes_read=len(payload))

    text = payload.decode("utf-8", errors="replace")
    missing = [key for key in smoke.expected_keys if key not in text]
    if missing:
        return SmokeResult(smoke.provider, skipped=False, ok=False, reason=f"missing expected keys: {missing}", bytes_read=len(payload))
    return SmokeResult(smoke.provider, skipped=False, ok=True, reason="ok", bytes_read=len(payload))


def run_default_smokes(enabled: bool | None = None) -> list[SmokeResult]:
    return [run_smoke_request(smoke, enabled=enabled) for smoke in default_smoke_requests()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run opt-in no-auth network smoke tests for public data sources.")
    parser.add_argument("--json", action="store_true", help="Emit JSON results")
    args = parser.parse_args()

    results = run_default_smokes()
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
        return
    for result in results:
        status = "SKIP" if result.skipped else "OK" if result.ok else "FAIL"
        print(f"{status} {result.provider}: {result.reason}")


if __name__ == "__main__":
    main()
