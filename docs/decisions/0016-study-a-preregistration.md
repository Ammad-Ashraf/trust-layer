# 0016 — Fix Study A's injections and tolerance before building the checks

- **Status:** decided
- **Date:** 2026-11-26
- **Decide by:** before M4 step 4 (writing C1–C5), about 2 Dec

## Question

Should Study A's list of injected errors and the C5 tolerance τ be fixed and committed now, before the checks exist, so the checker can't be tuned to its own test?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Fix now: the injection table and τ = 5% in `docs/design/checker-v0.md` §7, committed as-is | Study A can't be accused of being built to pass; every injection is grounded in an observed slip (M2, the Collider-Bench paper, the smoke run) | Locks us in; a missed error type can only be added later, reported as "added after" |
| B. Decide the injections after the checks are built | More freedom | A reviewer can say the test was designed around the checker; weakens the backbone claim |

## Claude's lean

A. Study A is the backbone claim. Fixing it first costs nothing and makes the catch rate credible. Additions stay possible, but they're reported separately.

## Decision (Ammad)

A, decided 2026-11-26. The injection table and τ = 5% in `docs/design/checker-v0.md` §7 are fixed as of this commit, so Study A's catch rate can't be said to be tuned to the checker. Any injection added later is reported separately as "added after".
