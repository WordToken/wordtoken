"""Regenerate golden fixtures for the parity contract.

Each fixture is four files in tests/fixtures/:
    {name}.input.jsonl     the corpus (committed by hand, never regenerated)
    {name}.taxonomy.yaml   copied here from taxonomies/ on every run
    {name}.expected.json   report JSON, generated_at frozen
    {name}.expected.md     report markdown, same freeze

Pipeline mirrors the CLI default: ingest -> scrub -> classify -> report.
The frozen timestamp keeps outputs byte-stable; any consumer (the TypeScript
port on wordtoken.com vendors this directory) must reproduce expected.json
structurally and expected.md exactly after the same normalization.

Run: uv run python scripts/make_fixtures.py
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wordtoken import Taxonomy, build_report, classify, from_jsonl, scrub

ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
TAXONOMIES = ROOT / "taxonomies"
FROZEN_NOW = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

# name -> canonical taxonomy file it runs against
FIXTURE_TAXONOMIES = {
    "smoke": "clipart-demand.yaml",
    "sample": "clipart-demand.yaml",
    "sample-visual-style": "visual-style.yaml",
    "sample-format": "format-and-usage.yaml",
    "unicode": "clipart-demand.yaml",
    "iterations": "clipart-demand.yaml",
    "other-heavy": "clipart-demand.yaml",
    "autojunk": "clipart-demand.yaml",
}

# fixtures that share another fixture's input corpus
INPUT_ALIASES = {
    "sample-visual-style": "sample",
    "sample-format": "sample",
}


def generate(name: str, taxonomy_file: str) -> None:
    input_path = FIXTURES / f"{INPUT_ALIASES.get(name, name)}.input.jsonl"
    if not input_path.exists():
        raise SystemExit(f"missing corpus: {input_path}")

    taxonomy_src = TAXONOMIES / taxonomy_file
    taxonomy_dst = FIXTURES / f"{name}.taxonomy.yaml"
    shutil.copyfile(taxonomy_src, taxonomy_dst)

    records = scrub(from_jsonl(input_path))
    report = build_report(
        classify(records, Taxonomy.load(taxonomy_dst)), now=FROZEN_NOW
    )
    (FIXTURES / f"{name}.expected.json").write_text(
        report.to_json() + "\n", encoding="utf-8"
    )
    (FIXTURES / f"{name}.expected.md").write_text(
        report.to_markdown(), encoding="utf-8"
    )
    print(
        f"  {name}: {report.corpus_size} records, "
        f"{len(report.bucket_counts)} buckets, "
        f"{len(report.warnings)} warnings"
    )


if __name__ == "__main__":
    FIXTURES.mkdir(parents=True, exist_ok=True)
    print("regenerating fixtures:")
    for name, taxonomy_file in FIXTURE_TAXONOMIES.items():
        generate(name, taxonomy_file)
