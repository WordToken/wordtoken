# Contributing

Thanks for looking at wordtoken. It's a small, deliberately-scoped library —
issues and PRs are welcome.

## Setup

```bash
git clone https://github.com/WordToken/wordtoken
cd wordtoken
uv sync            # installs the package + dev group
pre-commit install # ruff, codespell, pyproject validation on commit
```

## Running checks

```bash
uv run pytest --cov     # tests (coverage gate: 90%)
uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy             # strict type check
```

## Ground rules

- **Open an issue before a large PR** — scope is guarded here; a quick
  conversation saves you a rewrite.
- If your change alters any report output, rerun
  `uv run python scripts/make_fixtures.py` and commit the fixture diff —
  the fixtures are a parity contract for ports of the engine, and
  `tests/test_fixtures.py` fails on silent drift.
- Taxonomy contributions (new domain YAML files) are especially welcome and
  need no Python.
