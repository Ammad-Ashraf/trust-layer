# CMS-SUS-16-046 T5Wg_1750_1700 Signal Yield Report

## Summary

Predicted S_T^γ histogram for T5Wg benchmark at m(g̃)=1750 GeV, m(W̃)=1700 GeV, massless gravitino LSP, normalized to 35.9 fb⁻¹ at √s=13 TeV.

| S_T^γ bin (GeV) | Expected events |
|---|---|
| 600–800 | 0.091 |
| 800–1000 | 0.293 |
| 1000–1300 | 0.877 |
| > 1300 | 2.334 |
| **Total** | **3.595** |

## Simulation chain

### Event generation (MadGraph5 + Pythia8 + Delphes)

- **Matrix element**: `mg5_aMC` with MSSM_SLHA2 model, process `p p > go go`, 50 000 events, CTEQ6L1 PDF, m(g̃)=1750 GeV.
- **SLHA spectrum**: Wino NLSP at 1700 GeV (χ̃⁰₁ and χ̃±₁), gravitino LSP at 1 GeV (effectively massless). Gluino 3-body decays split 50%/50% to χ̃⁰₁ qq̄ and χ̃±₁ q′q̄; χ̃⁰₁→γG̃ and χ̃±₁→W±G̃ with BR=1 each. All squarks/sleptons decoupled at 5 TeV.
- **Parton shower**: Pythia8 (v8.312), tune CUETP8M1 (Tune:pp=14), ISR/FSR/MPI/hadronisation on. Gravitino set stable and invisible.
- **Detector simulation**: Delphes 3 with `delphes_card_CMS.tcl`. Anti-k_T jets (R=0.4), CMS-parametrized photon/lepton/jet resolutions and efficiencies.

### NLO cross section

Prospino 2.1, gluino pair (`gg`), NLO, CTEQ6, 13 TeV: **σ_NLO = 0.00268 pb = 2.68 fb** (K-factor ≈ 2.59).

## Event selection (CMS-SUS-16-046 signal region)

Applied in `analysis/analysis.py`:

1. **Photon selection**: pT > 180 GeV, |η| < 1.44 (barrel), ΔR(γ, jet) > 0.5 for jets with pT > 30 GeV.
2. **MET**: p_T^miss > 300 GeV.
3. **Transverse mass**: M_T(γ, MET) > 300 GeV (leading selected photon).
4. **Jet azimuthal angle**: |Δφ(MET, jet)| > 0.3 for all jets with pT > 100 GeV.
5. **S_T^γ > 600 GeV** (also the binning variable; S_T^γ = p_T^miss + Σ pT(selected photons)).

### Cutflow

| Cut | Events passing | Fraction |
|---|---|---|
| Total generated | 50 000 | 100% |
| MET > 300 GeV | 9 922 | 19.8% |
| ≥1 barrel photon pT>180, ΔR>0.5 | 4 112 | 8.2% |
| M_T(γ,MET) > 300 GeV | 3 453 | 6.9% |
| |Δφ(MET,jet)| > 0.3 | 2 257 | 4.5% |
| S_T^γ > 600 GeV | 2 256 | 4.5% |

Raw selection efficiency: **ε = 2256/50 000 = 4.51%**.

## Corrections applied

| Correction | Value | Source |
|---|---|---|
| Photon ID scale factor (data/Delphes) | 0.878 (average) | `photon_eff_LoosePixelVeto.root`: 0.848/0.95 (|η|<0.8), 0.809/0.95 (0.8<|η|<1.44) |
| Photon trigger efficiency | 0.943 | CMS-SUS-16-046 paper, ε_γ = 94.3±0.4% |

Combined correction × raw yield: 4.341 × 0.878 × 0.943 = **3.595 events**.

## Normalization accounting

σ × L × BR × ε × SF_phot × ε_trig = 2.68 × 35.9 × 1.0 × 0.04512 × 0.878 × 0.943 = **3.595** events (matches histogram sum).

## Deviations from paper

1. **Fast detector simulation (Delphes) instead of CMS FastSim/FullSim**: Delphes provides only a parametric simulation. Full CMS reconstruction would include pixel veto efficiency, isolation details, and η-dependent photon energy corrections not captured by Delphes. The photon ID SF partially corrects for this.

2. **Photon isolation in Delphes**: The CMS card applies a cone-based isolation cut (pT_ratio < 0.12 within ΔR < 0.5). The paper uses the CMS cut-based photon ID with pixel seed veto; the Delphes model is an approximation.

3. **No pile-up simulation**: The analysis was run without pile-up overlay. The paper applied pile-up reweighting to data; this affects MET resolution and jet multiplicity but is a minor effect for high-pT signal events.

4. **LO matrix element + NLO cross section**: MadGraph5 generates gluino pairs at LO; the NLO K-factor is applied via Prospino cross section reweighting. Full NLO matching (e.g. with MC@NLO) would affect kinematic distributions mildly.

5. **Fixed NLSP decay BRs in SLHA**: Since m(χ̃⁰₁) = m(χ̃±₁) = 1700 GeV (compressed spectrum), Pythia8 uses the SLHA decay table directly. χ̃⁰₁→γG̃ and χ̃±₁→W±G̃ with BR=1 is exact for massless gravitino LSP in GMSB-like T5Wg topology.

## Artifacts

| Artifact | Path |
|---|---|
| Analysis code | `analysis/analysis.py` |
| Entry point | `analysis.py` |
| Delphes output | `data/T5Wg_1750_1700.root` |
| SLHA spectrum (MG5) | `sims/T5Wg_1750_1700.slha` |
| SLHA spectrum (Pythia8) | `sims/pythia8_T5Wg.slha` |
| Delphes card | `sim/run_delphes_001/delphes_card.tcl` |
| Results histogram | `results/histogram_T5Wg.yaml` |
| Normalization ledger | `ledger.yaml` |
