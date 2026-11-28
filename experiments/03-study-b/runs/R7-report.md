# R7 · Study B, all 36 slots final

Setup tag `study-b-v1`, unchanged throughout. `git diff study-b-v1 HEAD` is empty for `src`, `integration`, `scripts`, `.gitmodules`, `config.yaml` and `schedule.yaml`. Outside run data and generated results it touches only `docs/` (decisions 0022 and 0023, runner tasks, outreach) and the launcher `experiments/03-study-b/usage_loop.py`.

- **Pilot (R6):** S01–S03 ran under `study_b.py next`.
- **S04 and S06:** ran under `study_b.py next` at the 0.40 usage pause.
- **S05 rerun and S07–S36:** ran under `experiments/03-study-b/usage_loop.py` at the 0.70 pause (decision 0023).

The last run (S36) finished 16:23 PKT 28 Nov, and the loop ended with "nothing left". Everything ran on Israr's Max subscription, $0 spend.

| Model | Arm | Slots | scored / timeout / crash | Voids | Wall-clock (sum) | Gate: pass / with warnings | Bounces |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sonnet 4.6 | baseline | 9 | 9 / 0 / 0 | 0 | 6.58 h | — | — |
| Sonnet 4.6 | checker | 9 | 9 / 0 / 0 | 2 (S05) | 8.33 h | 8 / 1 (S25) | 6 |
| Haiku 4.5 | baseline | 9 | 9 / 0 / 0 | 0 | 1.10 h | — | — |
| Haiku 4.5 | checker | 9 | 9 / 0 / 0 | 0 | 1.22 h | 8 / 1 (S22) | 12 |

**Total wall-clock:** 17.25 h over the 36 final runs. With S05's two void attempts (1.58 h + about 0.4 h) it comes to about 19.2 h. The longest run took 1.65 h (S14), far under the 10 h limit and the pilot's 8 h stop rule.

**Voids, both S05, both infrastructure (decision 0018):**
- **void1:** `gate_error`, because the agent's shell was in a subfolder. This is a known bug, [`GATE-BUG-cwd.md`](GATE-BUG-cwd.md), voided by hand as the runner tasks say.
- **void2:** I stopped the run on purpose because the laptop was being moved.

No checker run after that had `gate_error: true`, and no run hit the usage limit mid-run. I checked the `rate_limit` status in the transcripts of the runs that started near the 0.70 pause or ran across a window reset (S25, S32).

**Odd things, all in labels and `CHECKER-NOTES.md`, none changing an outcome:**
- **Scored with 0/4 bins:** S03 and S25. In both, the agent ended its turn to wait for a background shower, and `-p` mode then ended the session.
- **`submitted_with_warnings`:** two checker runs (S22, S25) reached the gate's bounce cap and passed with checks still failing.
- **`n_gen` is null in every manifest:** a code fix for after Study B, already listed.
