# 0021 — Study B is run, labelled and tabulated entirely on the runner

- **Status:** decided
- **Date:** 2026-11-27

## Question

Until now the Windows session reviewed every runner step (tag, pilot, labelling, results). Should Study B instead run to the end on Israr's laptop, in a Claude session on his Max plan?

## Decision (Ammad)

Yes. "From now onwards, to complete Study B, everything is on Israr's machine in his Max plan session, until Study B is complete."

## How it is made safe

- Every gate is a rule written before any run (runner tasks R5–R8): R5 pass → the runner tags `study-b-v1`; the pilot goes on to R7 only if all 3 runs are scored and each took under 8 h; anything else stops and comes back to Windows.
- The runner still never edits code or docs. CLAUDE.md now also lets it commit `experiments/03-study-b/results/` (generated only), append to `lab-log.md`, and create the one tag.
- `scripts/study_b.py` refuses measured runs if any code changed since the tag.
- Labelling on the runner uses the `label-run` skill; the hand ledgers stay out of the run folders.
