# trust-layer

A verification layer that checks the numbers AI agents produce in science, tested first in particle physics.

**Phase 1 (now):** a normalization checker for AI agents on [Collider-Bench](https://github.com/dfaroughy/Collider-Bench). It makes the agent record every physics number (cross-section, luminosity, branching fraction, efficiency) with its unit and source, then checks the ledger before the agent can submit. It targets the silent counting-math errors Collider-Bench found agents making: wrong units, wrong source, a missing factor, a mismatched input, or a right value that is never used.

## Status

| Milestone | Status |
| --- | --- |
| Repo + container setup, smoke run | In progress |
| Study A: error injection | Not started |
| Study B: with vs without checker (18 runs) | Not started |
| Technical note | Not started |

Full plan: [`docs/roadmap.md`](docs/roadmap.md).

## Results

None yet. The headline table goes here once Study A and Study B have numbers.

## Repository layout

```
docs/          project summary, roadmap, decisions, engineering standards, note
papers/        paper manifest + reading notes (PDFs fetched locally, not committed)
external/      Collider-Bench, as a pinned git submodule
src/           the trustlayer package: ledger, checks, gate, inject, report
tests/         unit tests
integration/   how the checker plugs into Collider-Bench
tasks/         per-task reference material (public sources only)
experiments/   one folder per experiment, with runs and results
scripts/       helper scripts
```

## Getting started

```bash
git clone --recurse-submodules <this repo>
cd trust-layer
python -m venv .venv
.venv/Scripts/activate         # Windows; on Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
python scripts/fetch_papers.py # optional: download reference papers into papers/pdf/
```
