# Changelog

All notable changes to wordtoken are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-08-12

First release of wordtoken as a prompt/brief demand-mining library.

> **Name history:** PyPI versions 0.1.x under this name were an unrelated,
> abandoned LLM-client experiment. They are yanked; pin `==0.1.2` only if you
> depended on the original. This library's API begins here.

### Added

- Pipeline: `ingest → scrub → classify → analyze → report`.
- Ingest adapters for JSONL, CSV, and dict rows with field mapping.
- PII scrubber (emails, URLs, card-like numbers, phone-like numbers) that
  runs by default before all other stages.
- Versioned YAML regex taxonomies (`Taxonomy.load`), with overlap-as-signal
  classification and an `other` catch-all.
- Analysis: term frequency with domain stopwords, bucket shares, and
  same-user iteration-chain detection.
- Reports: stable JSON (`schema_version: 1`) and markdown, with small-corpus
  and bloated-`other` warnings; `now` injection for reproducible output.
- CLI: `wordtoken report`, `--version`.
- Starter taxonomies: `clipart-demand`, `visual-style`, `format-and-usage`.
- Golden fixtures (`tests/fixtures/`) serving as the cross-language parity
  contract for engine ports.
- Typed package (`py.typed`), Python 3.10–3.14.

### Notes

- Python 3.10 reaches end of life 2026-10-31; the floor moves to 3.11 in a
  future minor release.

[Unreleased]: https://github.com/WordToken/wordtoken/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/WordToken/wordtoken/releases/tag/v1.0.0
