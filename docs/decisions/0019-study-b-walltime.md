# 0019 — Study B time limit on the runner laptop: 10 h, a pilot, and fixed timeout reporting

- **Status:** decided
- **Date:** 2026-11-27
- **Replaces:** item 3 of [0018](0018-study-b-zero-spend.md) ("raise the walltime later if needed")

## Question

Study B runs on a 32-thread laptop (0018). The paper gave each agent 128 cores and a 2.5 h limit. Will runs end by timeout instead of by real mistakes, and will that skew the comparison between the two arms?

## Facts

- The paper's Table 4 (128 cores): mean run time is Sonnet 4.6 **1.10 ± 0.37 h** and Haiku 4.5 **0.30 ± 0.25 h**, under the 2.5 h limit.
- On the laptop, the smoke run (Sonnet 4.6, T5Wg, agent chose N_gen = 10,000) took 27.8 min, and R2 (Haiku 4.5, checker arm) took 8.5 min.
- Only the simulation part of a run slows down on fewer cores; the agent's thinking time doesn't.
- **The real risk is lopsided timeouts.** The checker arm spends extra time on the ledger and up to 3 bounces, so it sits closer to the limit. A run that times out is scored on whatever template exists, so the checker would look worse for a reason that isn't physics.
- The agent is **not told** the limit: `task.toml` isn't exposed to it (`agent_runtime/workspace.py`), and the harness enforces the limit from outside (`_arm_walltime_watchdog`). Raising the limit therefore doesn't change how the agent plans.
- `bin/run-analysis` has its own 4 h timeout per call (`ANALYSIS_TIMEOUT=14400`). It is the same in both arms and is left unchanged.

## Decision (Ammad)

All three, decided 2026-11-27:

1. **Limit 10 h for both arms** (4× the paper's 2.5 h, on 1/4 of its cores: same total compute). Done in the fork (`Ammad-Ashraf/Collider-Bench@d8ac871`), only in the `task.toml` of the three Study B tasks (`sus-16-034_sim-TChiWZ`, `sus-16-046_sim-T5Wg`, `sus-16-051_sim-T2tt_comp`). Reported as a deviation from the paper.
2. **Pilot first:** one no-checker Sonnet 4.6 run per task. Record wall-clock, N_gen and how the run ended. If the setup is frozen (tag) before the pilot, these count as Study B's first three no-checker runs.
3. **Timeout reporting is fixed before any run:** report the timeout count per arm and the time the checker added per run (ledger calls plus bounces). Timed-out runs are scored as they are and **never rerun**. (Usage-limit or auth failures are void and rerun, per 0018; those are infrastructure failures, not the agent running out of time.)
