"""Reports — the artifact wordtoken exists to produce.

JSON for pipelines (stable schema, diffable in CI), markdown for humans.
Small-n honesty is baked in: bucket lines carry their absolute counts and
the report warns when the corpus is too small to treat shares as more
than direction.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .analyze import IterationGroup, bucket_shares, find_iterations, top_terms
from .classify import OTHER, Classification

SCHEMA_VERSION = 1
SMALL_N = 200


@dataclass
class Report:
    generated_at: str
    corpus_size: int
    taxonomy_name: str
    taxonomy_version: int
    bucket_counts: dict[str, int]
    bucket_shares: dict[str, float]
    bucket_samples: dict[str, list[str]]
    top_terms: list[tuple[str, int]]
    iteration_groups: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        lines = [
            f"# Demand report — {self.taxonomy_name} v{self.taxonomy_version}",
            f"\n{self.corpus_size} records · generated {self.generated_at}",
        ]
        for w in self.warnings:
            lines.append(f"\n> ⚠️ {w}")
        lines.append("\n## Buckets\n")
        lines.append("| bucket | records | share |")
        lines.append("|---|---|---|")
        for name, count in self.bucket_counts.items():
            lines.append(
                f"| {name} | {count} | {self.bucket_shares.get(name, 0):.0%} |"
            )
        lines.append("\n## Samples\n")
        for name, samples in self.bucket_samples.items():
            if samples:
                lines.append(f"**{name}**")
                # rstrip: truncation can cut mid-word and leave a trailing
                # space, which editors and hooks would silently strip.
                lines.extend(f"- {s.rstrip()}" for s in samples)
                lines.append("")
        lines.append("## Top terms\n")
        lines.append(", ".join(f"{w} ({c})" for w, c in self.top_terms))
        if self.iteration_groups:
            lines.append("\n## Iteration (same user refining one idea)\n")
            for g in self.iteration_groups[:10]:
                # deliberate typography, not a stray letter x
                lines.append(
                    f"- ×{len(g['texts'])}: {g['texts'][0][:80].rstrip()}"  # noqa: RUF001
                )
        return "\n".join(lines) + "\n"


def build_report(
    classification: Classification,
    *,
    extra_stopwords: frozenset[str] | set[str] = frozenset(),
    samples_per_bucket: int = 8,
    now: datetime | None = None,
) -> Report:
    """Build the report. `now` pins generated_at for reproducible fixtures."""
    records = [i.record for i in classification.items]
    counts = dict(sorted(classification.counts.items(), key=lambda kv: -kv[1]))

    warnings = []
    if len(records) < SMALL_N:
        warnings.append(
            f"Corpus has only {len(records)} records — treat shares as direction, not statistics."
        )
    other_share = counts.get(OTHER, 0) / len(records) if records else 0
    if other_share > 0.4:
        warnings.append(
            f"{other_share:.0%} of records matched no bucket — the taxonomy is missing "
            "what your users are asking for. Read the 'other' samples."
        )

    groups: list[IterationGroup] = find_iterations(records)
    return Report(
        generated_at=(now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
        corpus_size=len(records),
        taxonomy_name=classification.taxonomy_name,
        taxonomy_version=classification.taxonomy_version,
        bucket_counts=counts,
        bucket_shares=bucket_shares(classification),
        bucket_samples={
            name: classification.samples(name, samples_per_bucket) for name in counts
        },
        top_terms=top_terms(records, extra_stopwords=extra_stopwords),
        iteration_groups=[
            {"user_id": g.user_id, "texts": list(g.texts)} for g in groups
        ],
        warnings=warnings,
    )
