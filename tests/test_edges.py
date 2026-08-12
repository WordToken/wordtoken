"""Edge-case coverage: scrub patterns, taxonomy validation, ingest quirks,
report formatting, CLI."""

import json

import pytest

from wordtoken import (
    Taxonomy,
    build_report,
    classify,
    from_csv,
    from_dicts,
    make_record,
    scrub_text,
)
from wordtoken.cli import main

# --- scrub ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("mail zoë@exämple.com now", "mail <email> now"),
        ("call +1 (555) 018-2447 today", "call <phone> today"),
        ("see https://example.com/a?b=c please", "see <url> please"),
        ("card 4242 4242 4242 4242 on file", "card <number> on file"),
        ("1024x1024 transparent png", "1024x1024 transparent png"),
        ("est. 1998, 24 pieces", "est. 1998, 24 pieces"),
    ],
)
def test_scrub_cases(raw, expected):
    assert scrub_text(raw) == expected


# --- taxonomy ------------------------------------------------------------


def test_taxonomy_rejects_empty_patterns():
    with pytest.raises(ValueError, match="no patterns"):
        Taxonomy.from_dict({"name": "t", "version": 1, "buckets": {"bad": {}}})


def test_taxonomy_exclude_wins():
    t = Taxonomy.from_dict(
        {
            "name": "t",
            "version": 1,
            "buckets": {
                "schools": {"patterns": ["school"], "exclude": ["school of fish"]}
            },
        }
    )
    (bucket,) = t.buckets
    assert bucket.matches("back to school sale")
    assert not bucket.matches("a school of fish")


def test_taxonomy_defaults():
    t = Taxonomy.from_dict({"buckets": {"a": {"patterns": ["x"]}}})
    assert t.name == "unnamed"
    assert t.version == 0


# --- ingest --------------------------------------------------------------


def test_from_dicts_skips_blank_and_missing_text():
    records = from_dicts([{"text": "  "}, {"nope": 1}, {"text": "ok"}])
    assert [r.text for r in records] == ["ok"]


def test_from_csv(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text('text,user_id\n"a, with comma",u1\nplain,u2\n', encoding="utf-8")
    records = from_csv(p)
    assert [r.text for r in records] == ["a, with comma", "plain"]
    assert records[0].source == "c.csv"


def test_make_record_normalizes_naive_timestamps():
    r = make_record("x", timestamp="2026-01-01T05:00:00")
    assert r.timestamp is not None
    assert r.timestamp.tzinfo is not None


# --- report --------------------------------------------------------------


def test_report_empty_corpus():
    t = Taxonomy.from_dict(
        {"name": "t", "version": 1, "buckets": {"a": {"patterns": ["x"]}}}
    )
    report = build_report(classify([], t))
    assert report.corpus_size == 0
    assert report.bucket_shares == {}


def test_report_other_share_warning():
    t = Taxonomy.from_dict(
        {"name": "t", "version": 1, "buckets": {"a": {"patterns": ["zzz"]}}}
    )
    records = [make_record(f"unmatched {i}") for i in range(10)]
    report = build_report(classify(records, t))
    assert any("matched no bucket" in w for w in report.warnings)


# --- CLI -----------------------------------------------------------------


def test_cli_report_json(tmp_path, capsys):
    corpus = tmp_path / "c.jsonl"
    corpus.write_text('{"text": "halloween sticker", "user_id": "u1"}\n')
    taxonomy = tmp_path / "t.yaml"
    taxonomy.write_text(
        "name: t\nversion: 1\nbuckets:\n  seasonal:\n    patterns: [halloween]\n"
    )
    assert (
        main(["report", str(corpus), "--taxonomy", str(taxonomy), "--format", "json"])
        == 0
    )
    out = json.loads(capsys.readouterr().out)
    assert out["bucket_counts"]["seasonal"] == 1


def test_cli_empty_corpus_errors(tmp_path, capsys):
    corpus = tmp_path / "c.jsonl"
    corpus.write_text("")
    taxonomy = tmp_path / "t.yaml"
    taxonomy.write_text("name: t\nversion: 1\nbuckets:\n  a:\n    patterns: [x]\n")
    assert main(["report", str(corpus), "--taxonomy", str(taxonomy)]) == 1
    assert "no records" in capsys.readouterr().err
