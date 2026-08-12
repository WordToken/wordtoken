"""Classification — tiered by cost, deterministic first.

Tier 1 (this module): taxonomy regex matching. Free, instant, reproducible.
A record may land in several buckets; overlap is signal, not error. What
matches nothing goes to "other" — and a large "other" is a finding in
itself, not a failure (it is where unknown-unknowns live).

Tier 2 (planned): embedding clustering over the "other" bucket, so
unmatched demand names itself instead of hiding in a catch-all.
Tier 3 (planned): LLM labeling of Tier-2 clusters — cost O(clusters),
never O(rows) — with the resulting labels frozen back into the taxonomy
file so reruns stay deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .records import Record
from .taxonomy import Taxonomy

OTHER = "other"


@dataclass(frozen=True)
class Classified:
    record: Record
    buckets: tuple[str, ...]  # (OTHER,) when nothing matched


@dataclass
class Classification:
    taxonomy_name: str
    taxonomy_version: int
    items: list[Classified] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for item in self.items:
            for b in item.buckets:
                out[b] = out.get(b, 0) + 1
        return out

    def samples(self, bucket: str, n: int = 8) -> list[str]:
        return [i.record.text[:120] for i in self.items if bucket in i.buckets][:n]

    def in_bucket(self, bucket: str) -> list[Record]:
        return [i.record for i in self.items if bucket in i.buckets]


def classify(records: list[Record], taxonomy: Taxonomy) -> Classification:
    result = Classification(
        taxonomy_name=taxonomy.name, taxonomy_version=taxonomy.version
    )
    for r in records:
        hits = tuple(b.name for b in taxonomy.buckets if b.matches(r.text))
        result.items.append(Classified(record=r, buckets=hits or (OTHER,)))
    return result
