# 03-study-b

- **Status:** not started
- **Question:** Does the same agent make fewer normalization errors with the checker than without?
- **Setup:** Same agent, model and tasks; 3 runs each, without and with the checker. Sonnet 4.6 (18 runs) plus a Haiku 4.5 arm (18 runs), so 36 runs, one at a time on the runner laptop on Israr's Max subscription (token login, 0020), with a 10 h limit per run. Scored with Collider-Bench's evaluator and judge. Full settings: `config.yaml`.

## Rules fixed before the first run (decisions 0018, 0019)

1. **Pilot first:** one no-checker Sonnet 4.6 run per task (3 runs). Record wall-clock, N_gen and how each run ended. If the setup is tagged before the pilot, they count as Study B's first three no-checker runs.
2. **Timeouts:** scored as they are, **never rerun**. Report the timeout count per arm.
3. **Usage-limit or auth failures:** void, never scored, rerun in the same arm. Report the void count per arm.
4. **Checker time:** report the time the checker added per run (ledger calls plus bounces), so time pressure between arms is visible.
5. **Deviation from the paper**, stated in every table: 32 threads and 10 h, instead of 128 cores and 2.5 h.
- **Output:** δ_norm (median of 3), pass rate, shape score, per-sub-gap labels, cost and time per arm, bounces, N_gen.
- **Pinned:** Collider-Bench commit · container digest · model snapshot · hardware (fill in before the first measured run)
- **Run:** `python3 scripts/study_b.py next` on the runner (runner tasks R6, R7). Run order: `schedule.yaml` (fixed by seed; pilot first, then blocks by repetition). Each run folder is `runs/<slot>_<task>_<model>_<arm>_<rep>/`.

## Findings

None yet.
