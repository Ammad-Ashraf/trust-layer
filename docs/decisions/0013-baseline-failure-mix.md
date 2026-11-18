# 0013 — Check the baseline failure mix before fixing Study B tasks

- **Status:** open
- **Date:** 2026-11-18
- **Decide by:** before M6 task selection

## Question

The smoke run failed on ε (0.93% vs about 38.6%) with σ, L and units right, so C1–C5 would have passed it. If most baseline failures are ε or kinematics, Study B has little for the checker to catch. Do we measure that before committing Study B's tasks?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. About 3 cheap baseline runs (Sonnet, 3 tasks), labelled, to count 1a–1e vs other failures | Tells us early whether Study B has power | About $17 API-equivalent and 3 transcript reads |
| B. Rely on the paper's statement that normalization is "a recurring bottleneck" | No cost | The paper gives no counts, and its δ_norm mixes ε errors in with formula errors |

An ε-plausibility check (3c) goes to the parking lot, not Phase 1 (scope guard).

## Claude's lean

A. It fits M3 (baseline run, label errors) and costs little next to Study B.

## Decision (Ammad)

—
