"""Ingest adapters — anything in, Records out.

Ship the boring ones (JSONL, CSV, list-of-dicts); custom sources are a
three-line generator away. Field mapping is explicit so nobody has to
rename columns before using the library.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .records import Record, make_record


def from_dicts(
    rows: Iterable[dict[str, Any]],
    *,
    text_field: str = "text",
    timestamp_field: str | None = "timestamp",
    user_field: str | None = "user_id",
    source: str = "dicts",
) -> list[Record]:
    records = []
    for row in rows:
        text = row.get(text_field)
        if not text or not str(text).strip():
            continue
        records.append(
            make_record(
                str(text),
                timestamp=row.get(timestamp_field) if timestamp_field else None,
                user_id=str(row[user_field])
                if user_field and row.get(user_field)
                else None,
                source=source,
                metadata={k: v for k, v in row.items() if k != text_field},
            )
        )
    return records


def from_jsonl(path: str | Path, **kwargs: Any) -> list[Record]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    kwargs.setdefault("source", Path(path).name)
    return from_dicts(rows, **kwargs)


def from_csv(path: str | Path, **kwargs: Any) -> list[Record]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    kwargs.setdefault("source", Path(path).name)
    return from_dicts(rows, **kwargs)
