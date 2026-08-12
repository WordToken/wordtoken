"""Analysis over a classified corpus.

The operations that turn a classified pile into an answer: term
frequency, bucket shares, and iteration detection. Iteration detection
matters because one user refining "halloween pastel goth" four times is
one demand signal plus strong engagement — not four independent demands.
Naive counts conflate the two.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher

from .classify import Classification
from .records import Record

_BASE_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "with",
        "and",
        "or",
        "for",
        "to",
        "is",
        "are",
        "at",
        "by",
        "from",
        "as",
        "it",
        "its",
        "this",
        "that",
        "be",
        "was",
        "were",
        "will",
        "would",
        "could",
        "should",
        "i",
        "you",
        "your",
        "my",
        "we",
        "our",
        "me",
        "them",
        "they",
        "he",
        "she",
        "him",
        "her",
        "his",
        "hers",
        "make",
        "create",
        "want",
        "need",
        "like",
        "more",
        "very",
        "just",
    ]
)

_WORD = re.compile(r"[a-z][a-z-]+")


def top_terms(
    records: list[Record],
    n: int = 30,
    extra_stopwords: frozenset[str] | set[str] = frozenset(),
) -> list[tuple[str, int]]:
    """Frequency of meaningful words. Pass domain stopwords (for an image
    site: "clipart", "png", "background"…) or the top of the list is noise."""
    stop = _BASE_STOPWORDS | set(extra_stopwords)
    freq: Counter[str] = Counter()
    for r in records:
        for w in _WORD.findall(r.text.lower()):
            if len(w) > 2 and w not in stop:
                freq[w] += 1
    return freq.most_common(n)


def bucket_shares(classification: Classification) -> dict[str, float]:
    """Share of records touching each bucket. Sums past 1.0 when buckets
    overlap — report the overlap, don't hide it."""
    total = len(classification.items)
    if total == 0:
        return {}
    return {
        b: c / total
        for b, c in sorted(classification.counts.items(), key=lambda kv: -kv[1])
    }


@dataclass(frozen=True)
class IterationGroup:
    user_id: str | None
    texts: tuple[str, ...]


def find_iterations(
    records: list[Record],
    similarity: float = 0.75,
) -> list[IterationGroup]:
    """Near-duplicate runs by the same user — someone iterating on one idea.

    O(n²) within each user's records, which is fine at per-user volumes;
    revisit with shingling if a single user exceeds a few thousand records.
    """
    by_user: dict[str | None, list[Record]] = {}
    for r in records:
        by_user.setdefault(r.user_id, []).append(r)

    groups: list[IterationGroup] = []
    for user_id, user_records in by_user.items():
        if user_id is None or len(user_records) < 2:
            continue
        remaining = [r.text for r in user_records]
        while remaining:
            seed = remaining.pop(0)
            cluster = [seed]
            rest = []
            for t in remaining:
                if SequenceMatcher(None, seed.lower(), t.lower()).ratio() >= similarity:
                    cluster.append(t)
                else:
                    rest.append(t)
            remaining = rest
            if len(cluster) >= 2:
                groups.append(IterationGroup(user_id=user_id, texts=tuple(cluster)))
    return sorted(groups, key=lambda g: -len(g.texts))
