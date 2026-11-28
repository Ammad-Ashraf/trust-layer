Status: `DONE`

## What Was Done

Implemented the full CMS-SUS-16-046 signal prediction for T5Wg_1750_1700 (m(g̃)=1750 GeV, m(W̃/B̃)=1700 GeV, massless gravitino LSP) at 13 TeV, 35.9 fb⁻¹.

### Simulation chain

1. **SLHA spectrum** (`sims/T5Wg_1750_1700.slha`): Minimal MODSEL (only `1  0`), gluino decays 50% to qq+χ⁰₁ and 50% to qq'+χ±₁ via 8 explicit 3-body decay channels; χ⁰₁→γG̃ (100%); χ±₁→W±G̃ (100%). Squarks set to 10 TeV.

2. **Pythia8 generation** (`sims/generate_T5Wg.py`): 50,000 events, pp at 13 TeV, CP5 tune, processes `SUSY:gg2gluinogluino` + `SUSY:qqbar2gluinogluino`. Generator cross section: 1.787 fb.

3. **NLO cross section**: Prospino 2.1 at NLO with CTEQ6.6, gluino-pair production: σ_NLO = 3.05 fb (K=2.26 over LO=1.35 fb). Clean SLHA without inline comments used for Prospino Fortran reader.

4. **Delphes simulation** (`sims/delphes_card_CMS_T5Wg.tcl`): Standard CMS card patched to add gravitino (PDG 1000039, -1000039) with zero calorimeter energy fraction in both ECal and HCal, and to include gravitino in the NeutrinoFilter (so GenMissingET also captures it). Without this fix the standard CMS card assigns 100% HCal energy fraction by default to unknown PDG codes, causing gravitinos to be treated as 1700 GeV neutral hadrons instead of invisible particles.

5. **Event selection** (`analysis/analysis.py`): CMS-SUS-16-046 Table 1 cuts — photon pT>180 GeV, |η|<1.44, H/E<0.05; jet cleaning (ΔR>0.5); Δφ(MET,jet)>0.3 for hard jets; MET>300 GeV; MT(γ,MET)>300 GeV; S_T^γ=MET+ΣpT(γ)>600 GeV. Trigger efficiency applied as flat weight 94.3%.

### Results

| S_T^γ bin (GeV) | Raw events / 50k | Expected yield (35.9 fb⁻¹) |
|---|---|---|
| 600–800 | 198 | 0.41 |
| 800–1000 | 803 | 1.66 |
| 1000–1300 | 2804 | 5.79 |
| >1300 | 22876 | 47.24 |
| **Total** | **26681** | **55.10** |

Signal region efficiency: 53.4%. The distribution is dominated by the last bin as expected — with Δm=50 GeV the gluino decay quarks are very soft and each gravitino carries ~850 GeV pT, pushing S_T^γ well above 1300 GeV in most events.

### Normalization formula

N_expected = σ_NLO × L × BR × ε × ε_trig = 3.05 × 35.9 × 1.0 × 0.5336 × 0.943 ≈ 55.1 events

## Status

| Artifact | Status |
|---|---|
| `sims/T5Wg_1750_1700.slha` | Done — SLHA for Pythia8 generation |
| `sims/T5Wg_prospino.slha` | Done — clean SLHA for Prospino NLO |
| `sims/delphes_card_CMS_T5Wg.tcl` | Done — CMS card with gravitino invisibility fix |
| `sims/generate_T5Wg.py` | Done — Pythia8 generator script |
| `sims/T5Wg_events.hepmc` | Done — 50,000 generated events |
| `analysis/analysis.py` | Done — full CMS-SUS-16-046 event selection |
| `data/delphes_T5Wg.root` | Done — Delphes output |
| `results/histogram_T5Wg.yaml` | Done — filled with normalized yields |
| `ledger.yaml` | Done — all normalization factors recorded |

## Possible Issues

- **Compressed spectrum soft jets**: The 50 GeV gluino-NLSP mass gap makes decay quarks very soft (~25 GeV each in gluino rest frame). These are largely below the jet-pT threshold, which is physically correct — the signal topology is photon+MET with little hadronic activity from SUSY decays. ISR jets from Pythia8 provide the hadronic recoil.

- **Prospino K-factor**: K=2.26 is large. For m(g̃)=1750 GeV near the LHC kinematic limit, NLO corrections are enhanced. This is consistent with published SMS cross section tables.

- **Gravitino Delphes fix**: The standard Delphes CMS card has `EnergyFraction {0} {1.0}` as the HCal default for unlisted PDG codes. Any BSM neutral stable particle (gravitino, neutralino not in the explicit list) would be misidentified as a neutral hadron without explicit zero-fraction entries. This is a systematic limitation of generic Delphes cards for SUSY models with light gravitino LSP.

- **No pile-up**: Delphes was run without pile-up overlay. CMS-SUS-16-046 applies pile-up corrections; this is a known simplification in this fast-sim study.
