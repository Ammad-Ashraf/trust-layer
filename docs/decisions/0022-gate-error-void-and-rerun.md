# 0022 — Study B: a checker run with a gate error is void and rerun; code stays frozen

- **Status:** decided
- **Date:** 2026-11-27

## Question

S05 (Sonnet 4.6, checker, T5Wg) ended in `gate_error`: the agent stopped from a subfolder, the gate couldn't find its task context and let it stop unchecked ([`GATE-BUG-cwd.md`](../../experiments/03-study-b/runs/GATE-BUG-cwd.md)). Should R7 keep going with such runs voided and rerun, or stop, fix the gate, re-tag `study-b-v2` and redo the checker-arm runs?

## Facts

- The rule was fixed before Study B: `scripts/postrun_check.py` says a run with `gate_error` "is not valid for Study B". `scripts/study_b.py` doesn't apply it, so it is applied by hand (folder → `_voidN` plus `note.md`, the same procedure as a reboot).
- Voiding and rerunning keeps 3 reps per cell. It keeps only checker runs whose agent stopped from the workspace root: a mild selection effect, visible as the void count per arm in `results/study-b.md`.
- So far: 1 gate error in 2 Sonnet checker runs (S04 fine).

## Decision (the person at the runner, in the runner session)

**Keep going:** void and rerun gate-error runs; fix the gate after Study B. If gate errors become common (a slot voids 3 times, `next` stops), this comes back for a new call.
