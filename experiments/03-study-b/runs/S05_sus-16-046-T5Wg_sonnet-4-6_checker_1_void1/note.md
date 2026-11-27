# S05 attempt 1: void (gate_error)

The gate's second Stop check ended in `gate_error` at 01:45 UTC: the agent had `cd`'d into `workspace/sim/run_pythia8_001`, and the gate looks up the task context from the folder name of the hook's cwd (`src/trustlayer/gate/locate.py:41`), so it raised `no task context … matches run folder 'run_pythia8_001'` and let the agent stop unchecked (fail-open, by design). Its first check (00:42 UTC) had bounced the agent for a missing efficiency, and the final ledger still has no efficiency.

Rule fixed before Study B: `scripts/postrun_check.py` says a run with `gate_error` "is reported, but it is not valid for Study B", and `src/trustlayer/gate/hook.py` says it "is then marked invalid". `scripts/study_b.py` doesn't apply that rule (it filed the run as `scored`), so I voided it by hand with the same rename procedure as a reboot, and the slot is rerun like any other infrastructure failure (0018). Nothing in this folder was changed except the folder name and this note. Before voiding it scored δ_norm 1.0, pass false, judge QUESTIONABLE, 1.58 h.

S05 is rerun after S36, when `next` is started again: the running loop had already passed it. Bug write-up for the Windows session: `../GATE-BUG-cwd.md`.
