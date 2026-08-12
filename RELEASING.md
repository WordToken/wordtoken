# Releasing (maintainer checklist)

## One-time setup (before the first 1.0.0 release)

1. **PyPI Trusted Publisher** — pypi.org → project `wordtoken` → Manage →
   Publishing → Add GitHub publisher:
   - Owner: `WordToken` · Repository: `wordtoken`
   - Workflow filename: `release.yml` · Environment: `pypi`
2. **GitHub environment** — repo Settings → Environments → create `pypi` →
   enable **Required reviewers** and add yourself. Every release then needs
   an explicit approval click.
3. **Revoke the old PyPI API token** (the one in the local `.env` from the
   0.1.x era) — pypi.org → Account settings → API tokens. Trusted Publishing
   replaces it; delete the `.env` entries too.
4. **Yank the 0.1.x releases** — project → Manage → Releases → yank
   `0.1.0`, `0.1.1`, `0.1.2` with reason:
   > Unrelated predecessor project; the wordtoken name now hosts a different
   > library starting at 1.0.0. Pin ==0.1.2 if you need the original.
   Do NOT delete them (deleting breaks pinned installs permanently).
5. **Branch protection** — Settings → Branches → protect `main`, require the
   CI checks.

## Every release

1. Update `CHANGELOG.md` (move Unreleased → new version + date) and bump
   `version` in `pyproject.toml` and `__version__` in
   `src/wordtoken/__init__.py`.
2. `uv sync && uv run pytest --cov && uv run ruff check . && uv run mypy`
3. Sanity-check the artifact:
   ```bash
   uv build
   python -m zipfile -l dist/*.whl   # confirm py.typed + LICENSE present
   ```
4. Commit, then tag and push:
   ```bash
   git tag v1.0.0 && git push origin main v1.0.0
   ```
5. Approve the `pypi` environment run in the Actions tab. Done — the
   workflow builds, attests (PEP 740), and publishes.
6. Create the GitHub Release from the tag, pasting the changelog entry.
