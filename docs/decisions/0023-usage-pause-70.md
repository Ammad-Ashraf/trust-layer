# 0023 — Study B: start runs while five-hour usage is below 70% (was 40%)

- **Status:** decided
- **Date:** 2026-11-27

## Question

`config.yaml` (frozen) makes `study_b.py` start a run only while the Max plan's five-hour usage is below 0.40 (0018). At that limit about 3 Sonnet runs fit in each five-hour window, and the laptop then sits idle until the window resets. The goal is at least 18 runs (S01–S18) by Saturday 28 Nov. Should the pause go up?

## Facts

- The five-hour window is a fixed block, not a rolling one. On 27 Nov the probe read 0.42 from 07:35 until the reset at 10:10, so the laptop was idle for about 2.5 h.
- Usage per run, measured: S05 and S06 plus their judges and labelling took the window from 0 to 0.40. A Sonnet run takes about 10–25% of the window, and a Haiku test run about 2%. The seven-day usage was 0.15 after 8 runs.
- The pause only decides *when* a run starts. It doesn't change what the agent sees, the model, the time limit or the scoring, so runs before and after this decision can be compared.
- The risk: a run that reaches 100% mid-run is void (0018) and rerun. That costs time and adds to the void count per arm, but it doesn't bias the score.
- `config.yaml` and `scripts/` are frozen at `study-b-v1`, so the limit can't be changed there.

## Decision (the person at the runner, in the runner session)

**Raise the five-hour pause to 0.70** (seven-day stays 0.85), with no change to frozen files. A new launcher, `experiments/03-study-b/usage_loop.py`, does the usage probe itself at the new limit. It then calls the frozen `study_b.py run <slot> --no-probe` for the first non-final slot in schedule order, one run at a time. It replaces `study_b.py next` from S05's rerun on. Runs S01–S04 and S06 started under 0.40. A run that voids is retried only after a fresh probe.
