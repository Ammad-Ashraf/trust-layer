# 0004 — Repo layout

- **Status:** decided
- **Date:** 2026-11-13

## Decision

- **Layout:** `docs/ papers/ external/ src/ tests/ integration/ tasks/ experiments/ scripts/`, plus `CLAUDE.md`, `lab-log.md` and `README.md` at the root. See `CLAUDE.md` for the map.
- **Collider-Bench is a git submodule** at `external/collider-bench/`, pinned to one commit (`2986d8b`, 2 Sep 2026, added 13 Nov 2026) and never edited. The pin is the "Collider-Bench commit" every run must record. Our changes go in `integration/`.
- **Papers:** `papers/papers.yaml` (manifest) and `papers/notes/` are committed; the PDFs go in git-ignored `papers/pdf/`, rebuilt by `scripts/fetch_papers.py`. The repo will go public, and most arXiv licences don't allow redistributing PDFs.
- **Results live with their experiment** (`experiments/NN/results/`); the README shows the headline table.
- **Raw simulation files are never committed.** Whether to commit transcripts is decided after the smoke run, once we see their size.
- **Repo name `trust-layer`, private until the note is ready** (January).
- **The runner pushes run data directly to GitHub,** only under `experiments/*/runs/`.
