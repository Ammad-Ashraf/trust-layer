# 02-study-a

- **Status:** done, closed 2026-11-27 (tag `study-a-v2`, all inputs real). The first run on 26 Nov (tag `study-a-v1`) used stand-in LO values for two tasks. Runner task R4 replaced them with Prospino's LO; the catch and false-alarm counts didn't change.
- **Question:** Does the checker catch known injected errors, and how often does it raise false alarms?
- **Setup:** Correct hand ledgers from `tasks/` (public sources only), plus broken copies with one 1a–1e mistake each from `trustlayer.inject`. The list was fixed by decision 0016 before the checks existed; the 0017 rows are reported separately. No API or simulation cost.
- **Tasks:** `sus-16-034_sim-TChiWZ`, `sus-16-046_sim-T5Wg`, `sus-16-051_sim-T2tt_comp` (T2tt_comp rather than T2tt_SRG, see decision 0014).
- **Inputs:** [`config.yaml`](config.yaml): τ = 5%, and the two public numbers per task that the injections need. Sources are in [`sources.md`](sources.md).
- **Output:** [`results/study-a.md`](results/study-a.md) (tables, generated) and [`results/cases.yaml`](results/cases.yaml) (one row per case).
- **Rerun:** `python -m trustlayer.report study-a` (takes seconds; writes `results/`).
- **Pinned:** the code tag `study-a-v2`. Collider-Bench, the container and the model don't enter: nothing is simulated or run by an agent.

## Findings

1. **Every injected mistake was caught: 28/28 on the pre-registered list, plus 6/6 for the 0017 rows.** There were **0 false alarms** on 10 clean and near-miss copies (and 0/3 for 0017).
2. **This shows the checks do what they were designed to do. It doesn't show they catch real agents' mistakes.** The mistakes were chosen to be the counting kind. Study B measures real runs. R2 already showed what this design misses: a run that invents a self-consistent answer.
3. **C5 (bins vs ledger) does most of the work.** It fired on 31 of 34 injections and was the only check that fired on 9. **C1 never fired:** a valid unit on the wrong number (pb written as fb) is caught by C4 or C5, not C1. So 1a's "own check" catch rate is 0/6 while its total catch rate is 6/6. The note must say this plainly.
4. **C4 is the only check that sees small but real errors.** L = 36.1 instead of 35.9 is only 0.6% off, well under τ. C4 catches it by comparing with the task card.
5. **τ = 5% sits in a wide safe window** (exploratory sweep, not pre-registered):
   - Honest rounding moves the total by at most 1.1% (ε 0.42461 → 0.42 on T5Wg). That gives 1 false alarm at τ = 1%, none from 2%.
   - The smallest injected error that only C5 can see is 23.5%: bins left at the LO normalization (TChiWZ, Prospino K = 1.19). With the stand-in LO (v1) it was about 20%, and τ = 20% missed one case; with the real LO nothing is missed even at 20%.
   - Every value from 2% to 20% gives 100% caught and 0 false alarms.
6. **Two injections don't apply when BR really is 1** (T5Wg and T2tt are simplified models with BR = 1 by definition): "BR = 1 without a reason" and the "BR folded into ε" near-miss. They are listed as not applicable, not counted as catches.

## LO cross sections (runner R4, 27 Nov)

- From Prospino 2.1 in the benchmark's image (`runs/20261127-0032_prospino-lo/`):
  - stop 800 GeV: LO 15.9 fb, NLO 27.2 fb (K = 1.71);
  - wino C1N2 550 GeV: LO 23.09 fb, NLO 27.55 fb (K = 1.19).
- Prospino's NLO is 4.0% and 8.7% below the published NLO+NLL values. That is expected without NLL resummation, and it matters for Study B: an agent that uses Prospino NLO for TChiWZ lands 8.7% below the paper's normalization, which is above τ only if it is compared with the paper. C2 accepts Prospino NLO as a correct source.

## Notes from filling the hand ledgers

- **Cross-section order:** the 2017 papers used NLO+NLL, and the SUSY cross-section WG pages now show only NNLOapprox+NNLL (about 20% higher). The NLO+NLL tables were read from 2019 Wayback Machine copies of the WG twiki. Gluino at 1750 GeV: 3.598 fb (NNLOapprox: 4.342). Stop at 800 GeV: 28.33 fb (NNLOapprox: 34.82).
- **T5Wg cut flow:** CMS's table starts at 121.76 events, which implies σ = 3.392 fb, 5.7% below the WG's NLO+NLL value. The ledger keeps the WG σ and the table's final yield, so the 5.7% sits in ε. An agent that took σ × L from this table would land 5.7% off: just over τ.
- **T2tt_comp:** the compressed-region yields come from CMS-SUS-16-051 Additional Table 1, column 800/400 (2.3, 1.7, 1.7, 2.2 events). The table has no "all events" row, so ε = 7.9 / (σ × L).
