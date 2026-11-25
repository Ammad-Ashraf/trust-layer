# 0017 — Should C2 verify where sigma came from, not just its label?

- **Status:** decided
- **Date:** 2026-11-26
- **Decide by:** before Study B (M6). It doesn't block Study A: Study A takes minutes to rerun if C2 changes.

## Question

In the first real checker-arm run (04-gate-test R2, Haiku 4.5), the agent recorded σ = 0.15 fb with `source_type: prospino`. Prospino had never returned a value; the number was invented, about 200× below the public 30.17 fb. C2 passed it, because C2 checks only the label. Should C2 also check that a Prospino-labelled σ matches an actual Prospino result in the run?

## What we can check fairly

When the agent runs `bin/prospino run`, the tool writes its result into its scratch folder (`prospino_scratch/<process>-<hash>/prospino.dat`, plus the JSON on stdout). That folder is the agent's own visible output, so reading it obeys the fairness rule: only what the agent can see, never hidden answers.

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Keep C2 label-only; report the miss in the note | No scope change; Phase 1 stays "counting checks" | Our first real run shows the checker passing a 200× σ error with a false source label; a reviewer will ask about it |
| B. C2 checks Prospino claims: a σ labelled `prospino` must match the NLO value (within 1%) of a Prospino result in the run's scratch folder, and fails if there is none | Small (one function), uses only agent-visible output, turns "σ comes from Prospino" from a claim into a check; would have caught R2 | A small step into provenance (Gap 2, Phase 2's parking-lot topic); needs the scratch path inside the container; `paper` and `xsec_wg` labels stay unverified |
| C. Full provenance checking (σ, ε counts against ROOT files, bins against analysis output) | Catches fabrication broadly | That's Phase 2; too big before 15 Jan |

## Claude's lean

B. It's the narrowest change that makes C2 do what its name says, and the evidence for it comes from our own run, not a hypothetical. Study A would add the matching injection as "added after 0016". The note would report R2 honestly either way.

## Decision (Ammad)

B, decided 2026-11-26 ("Yes, add it"). Built the same day: `trustlayer/checks/prospino.py` reads finished `prospino_scratch/*/prospino.dat` files written since the run's `prompt.txt` (in the workspace and in the Collider-Bench root that `bin/prospino` works from). C2 then requires a Prospino-labelled σ to match one of their NLO values within 1%. R2's real ledger is a regression test (`tests/checks/test_prospino.py`).
