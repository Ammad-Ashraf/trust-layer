# 0014 — Drop the extra failure-mix runs (supersedes 0013)

- **Status:** decided
- **Date:** 2026-11-18

## Question

Decision 0013 added about 3 extra baseline runs to check whether AI mistakes are mostly "counting" (Gap 1) or "selection" (cuts, ε). Is that check needed?

## Why 0013 was wrong

- **It rested on one run.** One 28-minute run of one task can't overturn a gap that the Collider-Bench paper measured over hundreds of runs.
- **The paper already answers the question.** Table 2 (total error) and Table 3 (shape-only error) of the Collider-Bench paper show this:
  - For Opus 4.7 and Sonnet 4.6, the shape error is smaller than the total error in all 10 tasks.
  - Often the gap is large: TChiWg Sonnet 0.15 vs 0.93; T5Wg_highHT Opus 0.07 vs 1.43; T6gg_lowHT Opus 0.04 vs 11.3.
  - Shape right but total wrong means the scale is off, which is Gap 1 territory. The text names the causes: wrong process or mass point, mixed conventions, a rate not propagated.
- **Our smoke run is the exception, not the rule.** Its shape error was 0.92, against the paper's 0.15 ± 0.15 for Sonnet on this task. So it was a selection mistake (3b/3c), which is out of Phase 1 scope by design.
- **The plan already covers the risk.** The power risk was already named, with a cheaper fix: pick Study B tasks where the paper's tables show counting failures. That needs reading, not runs.

## Decision

- Drop the extra runs.
- M3 stays as planned: one baseline run, read in full and labelled.
- Use Tables 2 and 3 to choose Study B tasks.
- Decided by Claude (delegated). Ammad challenged 0013 and was right.

## What the tables say about our 3 target tasks

| Task | Opus 4.7 total / shape | Sonnet 4.6 total / shape | Counting gap? |
| --- | --- | --- | --- |
| sus-16-034 TChiWZ | 0.19 / 0.09 | 0.30 / 0.07 | yes |
| sus-16-046 T5Wg | 0.51 / 0.12 | 0.61 / 0.15 | yes |
| sus-16-051 T2tt_SRG | 0.42 / 0.40 | 0.53 / 0.52 | **no**: failures there are selection, not counting |
| sus-16-051 T2tt_comp (same paper) | 0.50 / 0.18 | 0.69 / 0.26 | yes |

Lean for Study B: swap `T2tt_SRG` for `T2tt_comp`, keeping the same paper. Confirm when the Study B model is chosen (0005).
