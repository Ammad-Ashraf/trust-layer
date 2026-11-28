Status: `DONE`

## What Was Done

Predicted binned differential signal yields in E_T^miss for T2tt (stop→t+χ̃₁⁰) with m(stop)=800 GeV, m(χ̃₁⁰)=400 GeV in the CMS-SUS-16-051 compressed signal region, normalized to 35.9 fb⁻¹ at √s=13 TeV.

### Simulation chain

1. **Hard scatter** — MadGraph5_aMC@NLO with MSSM_SLHA2 UFO model, process `p p > t1 t1~`, 50 000 unweighted events at LO. Stop and neutralino masses set in `sim/mg5_T2tt_800_400/Cards/param_card.dat`; stop forced to decay 100% to `t χ̃₁⁰`.

2. **Parton shower + hadronisation** — Pythia8 (v8.312, CMS UE tune CP1) reading the LHEF output. The χ̃₁⁰ (PID 1000022) is excluded from the HepMC3 output so Delphes reconstructs MET purely from momentum imbalance. Primary b- and c-quarks (first production, mother not same flavour) are written with HepMC status=3 so Delphes's `JetFlavorAssociation` module can fill `Jet.Flavor` and enable b-tagging.

3. **Detector simulation** — Delphes 3 with `delphes_card_CMS.tcl`. The 50 000-event HepMC3 file was split into five 10 000-event chunks to avoid OOM. Output: `sim/delphes_chunk{0-4}.root`.

4. **Analysis** — `analysis/analysis.py` (also `analysis.py` at workspace root):
   - Lepton selection: electrons pT>20 GeV |η|<1.442 iso<0.1; muons pT>20 GeV |η|<2.4 iso<0.1.
   - Jet selection: AK4 pT>30 GeV |η|<2.4; b-tag via Delphes `Jet.BTag` bit 0 (medium WP, ~65% eff).
   - **Preselection**: E_T^miss>250 GeV, exactly 1 lepton, N_jet≥2, ≥1 b-tag, M_T>150 GeV, minΔφ(J1,J2,MET)>0.5.
   - **Compressed selection (Table 3)**: N_jet≥5, leading jet not b-tagged, Δφ(MET,lep)<2, pT(lep)<150 GeV.

5. **Normalisation** — σ(NLO)=27.2 fb from Prospino 2.1 for stop-pair production at 800 GeV, 13 TeV. Expected yield = σ(NLO) × L × ε_bin, where ε_bin = N_pass_bin / N_gen.

### Results

| E_T^miss bin [GeV] | Raw events | Yield [events] |
|---|---|---|
| [250, 350) | 82 | 1.602 |
| [350, 450) | 77 | 1.504 |
| [450, 550) | 47 | 0.918 |
| [550, ∞)   | 70 | 1.367 |
| **Total**  | **276** | **5.391** |

Overall selection efficiency: 276 / 49 995 = 0.552%.

### Key systematic considerations

- **Generator-level**: LO matrix element only; no NLO/NLO+PS corrections to acceptance. The NLO K-factor is applied to the total cross section only.
- **B-tagging**: Delphes parameterised efficiency (~65% for b-jets, ~1% mistag for light jets). Real CMS applies data/MC scale factors not included here.
- **Fast-sim vs full-sim**: Delphes lacks charged-particle tracking resolution tails and trigger emulation; efficiency is an approximation.
- **Sample size**: 276 passing events give ~6% statistical uncertainty on the total yield.

## Status

| Artifact | Status |
|---|---|
| `sims/proc_card_T2tt.dat` | Done — MadGraph5 process card |
| `sim/mg5_T2tt_800_400/Cards/param_card.dat` | Done — MSSM_SLHA2 with m(stop)=800, m(χ̃₁⁰)=400 |
| `sims/shower.py` | Done — Pythia8 shower driver |
| `sims/split_hepmc.py` | Done — HepMC3 chunk splitter |
| `sim/T2tt_800_400.hepmc` | Done — 50 000 showered events |
| `sim/delphes_chunk{0-4}.root` | Done — Delphes output |
| `datasets.yaml` | Done — 5 chunk files, 49 995 events |
| `analysis/analysis.py` | Done — full selection + normalisation |
| `data/T2tt_800_400_selected.root` | Done — selected events |
| `results/histogram_T2tt_comp.yaml` | Done — 4-bin MET yields filled |
| `ledger.yaml` | Done — efficiency 0.00552 recorded |

## Possible Issues

- The compressed selection requires ISR recoil (N_jet≥5, leading jet not b-tagged). This makes the signal yield sensitive to the ISR jet-pT spectrum, which Delphes/Pythia8 may not model as precisely as CMS full simulation.
- MadGraph5 generates only `p p > t1 t1~` at LO; ISR radiation comes entirely from Pythia8's initial-state shower. CMS often uses dedicated MG5+MLM matched samples with explicit ISR jets for compressed regions.
