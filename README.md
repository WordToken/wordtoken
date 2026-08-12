# wordtoken

**Mine what your users actually want.**

[![CI](https://github.com/WordToken/wordtoken/actions/workflows/ci.yml/badge.svg)](https://github.com/WordToken/wordtoken/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wordtoken)](https://pypi.org/project/wordtoken/)
[![Python](https://img.shields.io/pypi/pyversions/wordtoken)](https://pypi.org/project/wordtoken/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Every AI product accumulates a pile of free-text user intent — prompts,
briefs, search queries. Reading five hundred of them by hand doesn't scale,
and dumping them into a chat model gives you a different answer every time.
wordtoken turns the pile into a reproducible answer: **who is showing up, and
what are they asking for?**

```python
from wordtoken import from_jsonl, scrub, Taxonomy, classify, build_report

records = scrub(from_jsonl("prompts.jsonl", text_field="prompt"))
taxonomy = Taxonomy.load("taxonomies/clipart-demand.yaml")
report = build_report(classify(records, taxonomy))
print(report.to_markdown())
```

Or the same thing as one command:

```bash
wordtoken report prompts.jsonl --taxonomy taxonomies/clipart-demand.yaml
```

```text
# Demand report — clipart-demand v1

200 records · generated 2026-01-01T00:00:00+00:00

## Buckets

| bucket | records | share |
|---|---|---|
| animals_nature | 62 | 31% |
| other | 42 | 21% |
| seller_commercial | 41 | 21% |
...
```

## Install

```bash
pip install wordtoken        # or: uv add wordtoken
```

Python 3.10+. One runtime dependency (PyYAML). Fully typed (`py.typed`).

## Why wordtoken

- **Deterministic.** Buckets are versioned YAML regex taxonomies. Same corpus
  + same taxonomy version = same numbers, every run. Reports are diffable in
  CI: alert when a demand segment crosses a threshold, not when a model's
  mood changes.
- **Local.** No network calls, no telemetry, no API keys. Your users'
  prompts never leave your machine.
- **Private by default.** A PII scrubber (emails, URLs, card-like and
  phone-like numbers) runs before every other stage, so everything
  downstream is safe to store and share. Skipping it is the flag
  (`--no-scrub`), not the default.
- **Honest at small n.** A 40-record corpus gets a "direction, not
  statistics" warning instead of false precision. A bloated catch-all bucket
  is flagged as the finding it is.
- **Iteration-aware.** One user refining *"halloween pastel goth"* four
  times is one demand signal plus strong engagement — not four independent
  demands. wordtoken groups those refinement chains instead of counting
  them.

## Usage

### Report from any corpus

JSONL, CSV, or plain dicts — map your field names instead of renaming
columns:

```python
from wordtoken import from_csv, from_dicts

records = from_csv("searches.csv", text_field="query", user_field="visitor")
records = from_dicts(rows, text_field="prompt", timestamp_field="created_at")
```

### Write a taxonomy for your domain

A taxonomy is data, not code — forking one requires no Python:

```yaml
name: my-product-demand
version: 1
buckets:
  power_users:
    description: Signals of heavy/API usage
    patterns: ["api", "bulk", "export", "automat"]
  educators:
    patterns: ["worksheet", "classroom", "grade \\d"]
    exclude: ["anime school"]   # matches that should NOT count
```

Records may match several buckets — overlap is signal, not error. Whatever
matches nothing lands in `other`, and a large `other` is where your
unknown-unknowns live: read its samples, grow the taxonomy, bump `version`.
Reports carry the taxonomy version so numbers from different versions never
get compared silently.

### Find iteration chains

```python
from wordtoken import find_iterations

for group in find_iterations(records):
    print(f"user {group.user_id} iterated {len(group.texts)} times:")
    print(f"  {group.texts[0]}")
```

### Diff demand over time

`Report.to_json()` has a stable schema (`schema_version: 1`) and a
`now`-injectable timestamp, so two runs over different time windows diff
cleanly:

```python
report = build_report(classification, now=frozen_time)  # reproducible output
```

## CLI

```text
usage: wordtoken report [-h] --taxonomy TAXONOMY [--text-field TEXT_FIELD]
                        [--user-field USER_FIELD]
                        [--timestamp-field TIMESTAMP_FIELD]
                        [--format {json,md}] [--no-scrub]
                        [--stopwords STOPWORDS]
                        corpus

positional arguments:
  corpus                path to a .jsonl or .csv corpus

options:
  -h, --help            show this help message and exit
  --taxonomy TAXONOMY   taxonomy YAML file
  --text-field TEXT_FIELD
  --user-field USER_FIELD
  --timestamp-field TIMESTAMP_FIELD
  --format {json,md}
  --no-scrub            skip PII scrubbing (not recommended)
  --stopwords STOPWORDS
                        comma-separated domain stopwords to drop from top
                        terms
```

Tip: pass domain stopwords or the top-terms list is noise — for an image
site that's `--stopwords "clipart,png,background,style"`.

## The pipeline

```
ingest → scrub → classify → analyze → report
```

Starter taxonomies ship in [`taxonomies/`](taxonomies/): demand, visual
style, and format/usage lenses for creative-tool prompts. The golden
fixtures in [`tests/fixtures/`](tests/fixtures/) double as the parity
contract for ports of the engine (the [wordtoken.com](https://wordtoken.com)
in-browser playground runs a TypeScript port verified against them).

Planned (tiers 2–3): clustering the `other` bucket with local embeddings so
unmatched demand names itself, and LLM labeling of those clusters — cost
scaling with clusters, never rows — with labels frozen back into the
taxonomy so reruns stay deterministic.

## Links

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [License](LICENSE) (MIT)

## History

PyPI versions **0.1.x were an unrelated earlier project** (an LLM-client
experiment) that happened to hold this name. This library begins at
**1.0.0**; do not depend on anything below it.
