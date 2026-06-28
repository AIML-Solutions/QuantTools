from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

from services.validation.models import AssetMasterRecord


@dataclass(frozen=True)
class ProviderRequest:
    provider: str
    assets: tuple[AssetMasterRecord, ...]
    purpose: str
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dry_run: bool = True


@dataclass(frozen=True)
class ProviderBatch:
    provider: str
    records: tuple[dict[str, Any], ...]
    retrieved_at: datetime
    source_metadata: dict[str, Any] = field(default_factory=dict)


class ProviderAdapter(Protocol):
    provider: str

    def fetch(self, request: ProviderRequest) -> ProviderBatch:
        """Return raw provider records without writing to storage or exposing secrets."""
