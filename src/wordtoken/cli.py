"""wordtoken CLI — one command from corpus to report.

wordtoken report corpus.jsonl --taxonomy taxonomies/clipart-demand.yaml
wordtoken report corpus.csv --text-field prompt --format md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .classify import classify
from .ingest import from_csv, from_jsonl
from .report import build_report
from .scrub import scrub
from .taxonomy import Taxonomy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wordtoken", description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    rep = sub.add_parser("report", help="classify a corpus and emit a demand report")
    rep.add_argument("corpus", help="path to a .jsonl or .csv corpus")
    rep.add_argument("--taxonomy", required=True, help="taxonomy YAML file")
    rep.add_argument("--text-field", default="text")
    rep.add_argument("--user-field", default="user_id")
    rep.add_argument("--timestamp-field", default="timestamp")
    rep.add_argument("--format", choices=["json", "md"], default="md")
    rep.add_argument(
        "--no-scrub", action="store_true", help="skip PII scrubbing (not recommended)"
    )
    rep.add_argument(
        "--stopwords",
        default="",
        help="comma-separated domain stopwords to drop from top terms",
    )

    args = parser.parse_args(argv)

    path = Path(args.corpus)
    loader = from_csv if path.suffix.lower() == ".csv" else from_jsonl
    records = loader(
        path,
        text_field=args.text_field,
        user_field=args.user_field,
        timestamp_field=args.timestamp_field,
    )
    if not records:
        print(
            f"no records found in {path} (text field: {args.text_field!r})",
            file=sys.stderr,
        )
        return 1
    if not args.no_scrub:
        records = scrub(records)

    taxonomy = Taxonomy.load(args.taxonomy)
    classification = classify(records, taxonomy)
    report = build_report(
        classification,
        extra_stopwords={w.strip() for w in args.stopwords.split(",") if w.strip()},
    )
    print(report.to_json() if args.format == "json" else report.to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
