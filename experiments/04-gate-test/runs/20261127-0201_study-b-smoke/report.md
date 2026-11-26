# R5 smoke, attempt 1: **fail** (judge did not run), no tag

Haiku 4.5, checker arm, sus-16-034_sim-TChiWZ, 02:01–02:11 PKT 27 Nov (0.158 h), token login, $0 on the subscription (API-equivalent $1.34).

Checks (R5 step 5–6):
- `outcome: scored` (not void) ✓ · `mcp_servers: []` ✓ · gate: 1 bounce, final pass, `tampered: false`, `gate_error: false` ✓
- `checker_time` filled (101.9 s, 11 record-quantity calls) ✓ · `score` filled (δ_norm 25.9, pass false) ✓
- **`judge: null` ✗**: no `judge_scores.json`. `eval.log` shows `launch_eval.sh` stopped at `activate_lhc_analysis: no harness-ready Python and conda not available`.
- Israr's own login still works (`claude -p … --model claude-haiku-4-5` answered) ✓

Cause: a runner setup problem, not a code bug. `launch_eval.sh` looks for a `python` with yaml/numpy/matplotlib/mplhep. This laptop has only `/usr/bin/python3`, no `python`, and the working venv at `external/collider-bench/.venv` wasn't on the unit's PATH. (The score itself came from the harness run, so it's unaffected.)

Fix (runner environment only, no code or doc changes): launch the units with `--setenv=PATH="$CB/.venv/bin:$PATH"` and `/usr/bin/python3 scripts/study_b.py …`. Checked: with that PATH, `python` is the venv and `ColliderBench.Evals.score` / `.judge` import cleanly. The Windows session may want to put this into the R5–R7 commands in `docs/runner-tasks.md`.

Next: R5 attempt 2 (a fresh smoke run with the fixed PATH). Tag `study-b-v1` only if all checks pass.
