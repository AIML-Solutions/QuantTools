from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from services.orchestration.research_plan import CostGuard, build_source_matrix, provider_from_record
from services.validation.models import AssetMasterRecord


def load_assets(path: Path) -> list[AssetMasterRecord]:
    return [AssetMasterRecord.model_validate(record) for record in json.loads(path.read_text())]


def load_providers(path: Path):
    return [provider_from_record(record) for record in json.loads(path.read_text())]


def generate_matrix(asset_master: Path, provider_catalog: Path, purpose: str, guard: CostGuard):
    return build_source_matrix(load_assets(asset_master), load_providers(provider_catalog), purpose, guard)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a dry-run source matrix from asset and provider fixtures.")
    parser.add_argument("--asset-master", default="examples/asset_master.example.json")
    parser.add_argument("--provider-catalog", default="examples/provider_catalog.example.json")
    parser.add_argument("--purpose", default="daily_baseline")
    parser.add_argument("--max-provider-calls", type=int, default=25)
    parser.add_argument("--max-records", type=int, default=5000)
    parser.add_argument("--max-raw-bytes", type=int, default=5_000_000)
    args = parser.parse_args()

    rows = generate_matrix(
        Path(args.asset_master),
        Path(args.provider_catalog),
        args.purpose,
        CostGuard(
            max_provider_calls=args.max_provider_calls,
            max_records=args.max_records,
            max_raw_bytes=args.max_raw_bytes,
        ),
    )
    print(json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
