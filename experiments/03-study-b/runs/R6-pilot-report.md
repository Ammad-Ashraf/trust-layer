# R6 · Study B pilot (S01–S03): **go** to R7

Sonnet 4.6, baseline (no checker), one run per task, setup tag `study-b-v1` (42404c8). One unit (`tl-pilot`) ran 02:23–04:28 PKT 27 Nov, $0 on the subscription. Launched with the venv on PATH (see `docs/runner-tasks.md`).

| Slot | Task | Outcome | Wall-clock | Δ_norm | Pass | Judge |
| --- | --- | --- | --- | --- | --- | --- |
| S01 | sus-16-034 TChiWZ | scored | 0.67 h | 0.094 | yes | VERIFIED, overrule NONE |
| S02 | sus-16-046 T5Wg | scored | 0.85 h | 0.265 | yes | VERIFIED, overrule NONE |
| S03 | sus-16-051 T2tt_comp | scored (0/4 bins) | 0.40 h | none | no | VERIFIED, overrule NONE |

**Go/no-go (0019):** all 3 `scored`, all under 8 h (longest 0.85 h, near the paper's 1.10 ± 0.37 h for Sonnet) → **go**.

**S03, worth Ammad's attention.** The agent restarted its 50k-event shower as a *background* job, wrote "I'll be notified when it finishes", and ended its turn (`stop_reason: end_turn`, `terminal_reason: completed`, 161 turns). In headless `-p` mode that ends the session. Collider-Bench's runner then printed `claude stalled 15s after result event; terminating session`, the shower was killed, and the run was filed as "exited cleanly but produced no filled bins". It isn't a usage, login or time problem, so by the frozen rules it is `scored`, final, never rerun. I didn't change that: changing outcome rules after seeing a result would break fairness.
- **Possible confound between arms:** in the checker arm, the Stop-hook gate fires when the agent ends its turn and can bounce it back if the ledger is incomplete. So the gate may rescue some early stops for reasons that have nothing to do with normalization. Suggest counting, per arm, the runs that end on an early "waiting for background job" stop, and gate bounces that came after such a stop, and reporting them next to the main table. This can be done from the transcripts during R8 labelling without any code change.
- S03's σ = 6.82 fb is ≈4× below the reference 28.33 fb. Labelled in R8 (1d, plus 1e: the agent's own Prospino NLO gave 27.2 fb and it discarded that). Correction to the judge's text: MG5 did *not* give ≈27 fb (its σ includes BR² = 4.4%); only Prospino did.

**Other notes:** `n_gen` is `null` in all three manifests: the script doesn't fill it. N_gen is read from the transcripts during labelling (S01 50k, S02 20k, S03 50k planned). This needs a code fix after Study B, not now. Each manifest's `trust_layer_commit` is the HEAD at launch, and HEAD moves as runs commit. `git diff study-b-v1 HEAD` touches only `experiments/03-study-b/{runs,results}/`, so the code is unchanged since the tag.
