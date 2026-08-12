"""Taxonomies as data, not code.

A taxonomy is a versioned YAML file of named buckets, each defined by
regex patterns (and optional exclusions). Same corpus + same taxonomy
version = same numbers, every run — that determinism is the whole point,
and it is what makes reports diffable in CI and trustworthy over time.

This is also the community-contribution surface: forking a taxonomy for
your domain requires no Python.

Format:

    name: clipart-demand
    version: 1
    buckets:
      educational:
        patterns: ["worksheet", "phonics", "grade \\d"]
        exclude: ["anime school"]      # optional
        description: "Teaching material"   # optional
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Bucket:
    name: str
    pattern: re.Pattern[str]
    exclude: re.Pattern[str] | None = None
    description: str = ""

    def matches(self, text: str) -> bool:
        if not self.pattern.search(text):
            return False
        return not (self.exclude and self.exclude.search(text))


@dataclass(frozen=True)
class Taxonomy:
    name: str
    version: int
    buckets: tuple[Bucket, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Taxonomy:
        buckets = []
        for bucket_name, spec in (data.get("buckets") or {}).items():
            patterns = spec.get("patterns") or []
            if not patterns:
                raise ValueError(f"bucket {bucket_name!r} has no patterns")
            joined = "|".join(f"(?:{p})" for p in patterns)
            exclude_list = spec.get("exclude") or []
            exclude = (
                re.compile("|".join(f"(?:{p})" for p in exclude_list), re.IGNORECASE)
                if exclude_list
                else None
            )
            buckets.append(
                Bucket(
                    name=bucket_name,
                    pattern=re.compile(joined, re.IGNORECASE),
                    exclude=exclude,
                    description=spec.get("description", ""),
                )
            )
        return cls(
            name=data.get("name", "unnamed"),
            version=int(data.get("version", 0)),
            buckets=tuple(buckets),
        )

    @classmethod
    def load(cls, path: str | Path) -> Taxonomy:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(yaml.safe_load(f))
