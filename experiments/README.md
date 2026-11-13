# Experiments

One folder per experiment, numbered in the order they run. Each has a `README.md` (question, setup, findings), a `config.yaml`, `runs/` and `results/`.

## A run folder: `runs/<run-id>/`

`run-id` = `YYYYMMDD-HHMM_<task>_<arm>_<n>`, e.g. `20261120-1430_sus-16-034_baseline_1`. Create one with `python scripts/new_run.py <experiment> <task> <arm>`.

| File | Committed | What |
| --- | --- | --- |
| `manifest.yaml` | yes | Pins and measurements (below) |
| `labels.yaml` | yes | Every mistake found, with a sub-gap code |
| submitted YAML + evaluator output | yes | Copied from the harness |
| gate bounce log | yes | Checker arm only |
| `raw/` | **no** | Simulation output, scratch; transcripts until we decide (decision 0004) |

`manifest.yaml` records: experiment, task, arm, model snapshot ID, Collider-Bench commit, container image digest, machine + cores, N_gen, wall-clock, tokens, API cost, bounce count, outcome (scored / timeout / crash).

**Report every run,** including failures. Results tables in `results/` are produced by `trustlayer.report`, never edited by hand.

The runner laptop commits only inside `runs/`.
