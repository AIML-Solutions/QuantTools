from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from services.ingestion.network_smoke import ENABLE_NETWORK_ENV, SmokeResult, run_default_smokes


def build_report(results: list[SmokeResult]) -> dict[str, object]:
    checks = [asdict(result) for result in results]
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "public_no_auth_smoke",
        "network_tests_env": ENABLE_NETWORK_ENV,
        "summary": {
            "checks_total": len(results),
            "checks_ok": sum(1 for result in results if result.ok),
            "checks_skipped": sum(1 for result in results if result.skipped),
            "checks_failed": sum(1 for result in results if (not result.ok and not result.skipped)),
        },
        "checks": checks,
        "caveat": "Point-in-time readiness artifact. Not an uptime SLA, entitlement proof, trading signal, or full feed validation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a compact public-safe smoke report artifact.")
    parser.add_argument("--out", default="examples/smoke-report.latest.json")
    args = parser.parse_args()

    report = build_report(run_default_smokes())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[smoke-report] wrote {out}")


if __name__ == "__main__":
    main()
