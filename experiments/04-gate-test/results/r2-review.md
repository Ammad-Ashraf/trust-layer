# R2 review: the first real checker-arm run (2026-11-26)

One Haiku 4.5 run of `simple_ledger` on `sus-16-034_sim-TChiWZ`. It's a plumbing test, not a measured run. Labels: [`labels.yaml`](../runs/20261126-0125_sus-16-034_checker_1/labels.yaml).

## The plumbing works

- **The launcher and the setup worked:** `scripts/run-checker-arm` launched our agent through Collider-Bench's own code, and the gate settings were installed in the workspace.
- **The agent used the ledger:** it called `bin/record-quantity`, and the CLI refused three bad entries on the spot. Those were an unknown process name `nn`, a BR of 1 with no reason, and a missing source. The agent fixed each one.
- **The gate fired at the end:** it ran all five checks, logged the decision, and wasn't tampered with.
- **Together with R1:** R1 ok 6 showed the gate *sending an agent back* in a real Claude Code session. **M4's mechanism is proven end to end.**

## The checker passed a fabricated answer

In the fishing picture, the agent's net caught **nothing** (0 of 50,000 events passed). So it wrote down a believable catch, a believable net size and a believable fish count, all consistent with each other. Our checker is a spell-checker for the arithmetic, and the arithmetic of a made-up answer can be perfect.

| Ledger entry | What the agent claimed | What actually happened |
| --- | --- | --- |
| σ | 0.15 fb, "Prospino 2, NLO" | Prospino never returned a number; public value 30.17 fb (200× higher) |
| ε | 0.11, n_pass/n_gen = 1/9 | 0 events passed; 0.11 is a product of guessed percentages, and 1/9 was invented to match it |
| bins | 0.20 / 0.22 / 0.14 / 0.04 | written by hand |
| BR | 1, with a reason | fine |
| L | 35.9 fb⁻¹ | fine |

All five checks passed, as designed: C1–C5 test consistency and labels, and a consistent fabrication passes them.

## What this means

- **It's Gap 2 (fabrication), which Phase 1 doesn't target.** The Collider-Bench paper found that about 6% of runs fabricate, mostly with cheap models like Haiku. Our first Haiku run happens to be one of them.
- **It is still a 200× σ error that C2 let through.** C2 trusts the label `prospino`. Decision [0017](../../../docs/decisions/0017-verify-sigma-provenance.md) (decided B, built 26 Nov): C2 now checks Prospino-labelled values against Prospino's actual output in the run. On R2's real ledger it fails with "no finished Prospino result" (regression test `tests/checks/test_prospino.py`). The invented ε and bins would still pass; that part is Phase 2 provenance.
- **For the note:** we report it as it is. The checker caught 0 of the run's 6 labelled mistakes, because none of them was a counting mistake in an honest pipeline. This is also evidence that the provenance check (the Phase 2 candidate) is needed.
- **For Study B:** with Haiku, fabrication may dominate. That bears on the Haiku-arm decision (0007).
