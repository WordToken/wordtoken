"""PII scrubbing — stage zero, always.

Prompts are user data. Scrubbing runs before classification, before
caching, before any report is written, so the corpus downstream of this
stage is safe to store, share, or send to a labeling model. Deliberately
conservative and deterministic: regex only, no network, no models.
"""

from __future__ import annotations

import re

from .records import Record

# Order matters: the card pattern must run before the phone pattern, or a
# 16-digit card number reads as a very long phone number.
_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"https?://\S+"), "<url>"),
    # Credit-card-ish: 13-16 digits in groups of 4.
    (re.compile(r"\b(?:\d{4}[\s-]?){3}\d{1,4}\b"), "<number>"),
    # Phone-ish: 7-15 digits with up to two separator chars between digits
    # (") " and ", " both occur in the wild). Digit-anchored at both ends so
    # no surrounding whitespace is eaten, and guarded against the x in
    # dimensions ("1024x1024") and against digit runs already inside one.
    (re.compile(r"(?<![\dx])\+?\(?\d(?:[\s().-]{0,2}\d){6,14}(?![\dx])"), "<phone>"),
]


def scrub_text(text: str) -> str:
    for pattern, token in _PATTERNS:
        text = pattern.sub(token, text)
    return text


def scrub(records: list[Record]) -> list[Record]:
    """Return scrubbed copies; user_id is kept (it is a join key, not PII in
    the corpus — hash it upstream if your ids are emails)."""
    out = []
    for r in records:
        clean = scrub_text(r.text)
        out.append(
            Record(
                text=clean,
                timestamp=r.timestamp,
                user_id=r.user_id,
                source=r.source,
                metadata=r.metadata,
            )
        )
    return out
