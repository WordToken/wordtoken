"""The golden fixtures are the parity contract (the TypeScript port on
wordtoken.com vendors tests/fixtures/ and must reproduce them). This test
regenerates every fixture in memory and diffs against what is committed,
so any engine or taxonomy change that would silently break parity fails here
first — the fix is to rerun scripts/make_fixtures.py and commit the diff
deliberately."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from wordtoken import Taxonomy, build_report, classify, from_jsonl, scrub

ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
FROZEN_NOW = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

NAMES = sorted(
    p.name.removesuffix(".expected.json") for p in FIXTURES.glob("*.expected.json")
)

# Mirrors scripts/make_fixtures.py INPUT_ALIASES.
INPUT_ALIASES = {"sample-visual-style": "sample", "sample-format": "sample"}


def regenerate(name: str) -> tuple[str, str]:
    corpus = FIXTURES / f"{INPUT_ALIASES.get(name, name)}.input.jsonl"
    records = scrub(from_jsonl(corpus))
    taxonomy = Taxonomy.load(FIXTURES / f"{name}.taxonomy.yaml")
    report = build_report(classify(records, taxonomy), now=FROZEN_NOW)
    return report.to_json() + "\n", report.to_markdown()


def test_fixture_set_is_nonempty():
    assert len(NAMES) >= 8


@pytest.mark.parametrize("name", NAMES)
def test_fixture_matches_committed(name):
    got_json, got_md = regenerate(name)
    expected_json = (FIXTURES / f"{name}.expected.json").read_text(encoding="utf-8")
    expected_md = (FIXTURES / f"{name}.expected.md").read_text(encoding="utf-8")
    assert json.loads(got_json) == json.loads(expected_json), (
        f"fixture {name!r} drifted — rerun scripts/make_fixtures.py and commit"
    )
    assert got_md == expected_md


def test_fixture_taxonomies_match_canonical():
    """The taxonomy copies in fixtures/ must not drift from taxonomies/."""
    canonical = {
        p.name: p.read_text(encoding="utf-8")
        for p in (ROOT / "taxonomies").glob("*.yaml")
    }
    for copy in FIXTURES.glob("*.taxonomy.yaml"):
        text = copy.read_text(encoding="utf-8")
        assert text in canonical.values(), (
            f"{copy.name} does not match any canonical taxonomy — "
            "rerun scripts/make_fixtures.py"
        )


def test_sample_fixture_health():
    """The sample corpus feeds the wordtoken.com hero — keep it warning-free
    and interesting."""
    report = json.loads((FIXTURES / "sample.expected.json").read_text())
    assert report["corpus_size"] == 200
    assert report["warnings"] == []
    assert len(report["iteration_groups"]) >= 4
    assert set(report["bucket_counts"]) >= {
        "educational",
        "seller_commercial",
        "holiday_seasonal",
        "animals_nature",
        "kids_characters",
        "other",
    }
