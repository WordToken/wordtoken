"""The one record shape every stage speaks.

Everything wordtoken ingests — generation prompts, pack briefs, search
queries, support tickets — normalizes to Record before any other stage
sees it. Adapters produce Records; classify/analyze/report consume them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Record:
    text: str
    timestamp: datetime | None = None
    user_id: str | None = None
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


def make_record(
    text: str,
    *,
    timestamp: str | datetime | None = None,
    user_id: str | None = None,
    source: str = "unknown",
    metadata: dict[str, Any] | None = None,
) -> Record:
    """Normalize loosely-typed inputs (ISO strings, missing fields) to a Record."""
    ts: datetime | None
    if isinstance(timestamp, str):
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    else:
        ts = timestamp
    if ts is not None and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return Record(
        text=text.strip(),
        timestamp=ts,
        user_id=user_id,
        source=source,
        metadata=metadata or {},
    )
