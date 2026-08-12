"""wordtoken — mine what your users actually want.

Pipeline: ingest → scrub → classify → analyze → report.

    from wordtoken import from_jsonl, scrub, Taxonomy, classify, build_report

    records = scrub(from_jsonl("prompts.jsonl", text_field="prompt"))
    taxonomy = Taxonomy.load("taxonomies/clipart-demand.yaml")
    report = build_report(classify(records, taxonomy))
    print(report.to_markdown())
"""

from .analyze import bucket_shares, find_iterations, top_terms
from .classify import Classification, Classified, classify
from .ingest import from_csv, from_dicts, from_jsonl
from .records import Record, make_record
from .report import Report, build_report
from .scrub import scrub, scrub_text
from .taxonomy import Bucket, Taxonomy

__version__ = "1.0.0"

__all__ = [
    "Bucket",
    "Classification",
    "Classified",
    "Record",
    "Report",
    "Taxonomy",
    "bucket_shares",
    "build_report",
    "classify",
    "find_iterations",
    "from_csv",
    "from_dicts",
    "from_jsonl",
    "make_record",
    "scrub",
    "scrub_text",
    "top_terms",
]
