"""End-to-end smoke test: dicts → scrub → classify → report."""

from pathlib import Path

from wordtoken import (
    Taxonomy,
    build_report,
    classify,
    find_iterations,
    from_dicts,
    scrub,
    scrub_text,
)

TAXONOMY = Path(__file__).parent.parent / "taxonomies" / "clipart-demand.yaml"

ROWS = [
    {
        "text": "first grade phonics worksheet borders",
        "user_id": "u1",
        "timestamp": "2026-08-01T10:00:00Z",
    },
    {
        "text": "halloween pastel goth pack",
        "user_id": "u2",
        "timestamp": "2026-08-02T10:00:00Z",
    },
    {
        "text": "halloween pastel goth pack, less orange",
        "user_id": "u2",
        "timestamp": "2026-08-02T10:05:00Z",
    },
    {
        "text": "kawaii ghost sticker",
        "user_id": "u3",
        "timestamp": "2026-08-03T10:00:00Z",
    },
    {
        "text": "contact me at zev@example.com",
        "user_id": "u4",
        "timestamp": "2026-08-04T10:00:00Z",
    },
    {
        "text": "isometric town blocks",
        "user_id": "u5",
        "timestamp": "2026-08-05T10:00:00Z",
    },
]


def test_pipeline_end_to_end():
    records = scrub(from_dicts(ROWS))
    taxonomy = Taxonomy.load(TAXONOMY)
    assert taxonomy.name == "clipart-demand"

    classification = classify(records, taxonomy)
    counts = classification.counts
    assert counts["educational"] == 1
    assert counts["holiday_seasonal"] == 2
    # kawaii ghost sticker overlaps seller + kids buckets
    assert counts["seller_commercial"] == 1
    assert counts["kids_characters"] == 1
    assert counts["other"] >= 1

    report = build_report(classification)
    assert report.corpus_size == len(ROWS)
    assert any("direction, not statistics" in w for w in report.warnings)
    assert report.to_markdown().startswith("# Demand report")
    assert '"schema_version": 1' in report.to_json()


def test_scrub_removes_pii_keeps_dimensions():
    assert "<email>" in scrub_text("mail zev@example.com please")
    assert scrub_text("1024x1024 transparent png") == "1024x1024 transparent png"


def test_iteration_detection_groups_refinements():
    records = from_dicts(ROWS)
    groups = find_iterations(records)
    assert len(groups) == 1
    assert groups[0].user_id == "u2"
    assert len(groups[0].texts) == 2
