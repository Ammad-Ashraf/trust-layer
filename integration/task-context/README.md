# Task context

One file per Collider-Bench task: the public facts checks C4 (match) and C5 need. They cover the benchmark's production process, the masses the cross section depends on, the full mass point, and the luminosity.

**Agent-visible facts only.** Every value here is copied from that task's `TASK.md` and results template, which the agent itself reads. These files may therefore be mounted into the container (they ship inside the `simple_ledger` agent folder). Reference yields, efficiencies and anything from `tasks/` (our hand-filled answer keys) never go here; `tests/test_fairness.py` checks this.

Names follow `src/trustlayer/ledger/names.py` (`gluino`, `chargino_1`, `stop_1`, ...; processes `gluino_pair`, `chargino_neutralino`, ...).
