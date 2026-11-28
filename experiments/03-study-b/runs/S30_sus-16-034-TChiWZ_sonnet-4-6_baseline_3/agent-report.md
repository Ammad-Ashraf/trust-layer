# Analysis Report: CMS-SUS-16-034 VZ Signal Region — TChiWZ_550_200

## Summary

Predicted signal yields for `TChiWZ_550_200` (pp → χ̃⁺₁ χ̃⁰₂, m=550/550 GeV, m(χ̃⁰₁)=200 GeV) in the CMS-SUS-16-034 electroweak VZ signal region, normalised to 35.9 fb⁻¹ at √s = 13 TeV.

| E_T^miss bin [GeV] | Signal yield [events] |
|---|---|
| 100 – 150 | 0.464 |
| 150 – 250 | 1.047 |
| 250 – 350 | 1.270 |
| > 350     | 1.322 |
| **Total** | **4.103** |

## Simulation Chain

### 1. Matrix-element generation (MadGraph5_aMC@NLO 3.7.0)

- Model: MSSM_SLHA2 UFO
- Process: `p p > x1+ n2` + `p p > x1- n2` (production only, no decays in MG5)
- Motivation: in the pure wino-bino limit (N₁₁=1, N₂₂=1), both χ̃⁺₁→Wχ̃⁰₁ and χ̃⁰₂→Zχ̃⁰₁ tree-level vertices vanish. Production via W* (pp→χ̃⁺₁χ̃⁰₂) is non-zero. Decays are handled by Pythia8.
- 50,000 events generated
- LO cross section from MG5: σ_LO = 0.02028 pb (sum of both charge states)
- Param card: `sims/TChiWZ_550_200.slha` derived from MG5 default MSSM card with m(χ̃⁰₁)=200 GeV, m(χ̃⁰₂)=m(χ̃⁺₁)=550 GeV, all other sparticles at 5 TeV

### 2. Parton shower and hadronisation (Pythia8 8.312)

- CMS UE tune CP1 (`Tune:pp = 14`)
- SLHA file `sims/TChiWZ_550_200_pythia.slha` with explicit DECAY blocks:
  - χ̃⁰₂ → Z χ̃⁰₁ (100% BR)
  - χ̃⁺₁ → W⁺ χ̃⁰₁ (100% BR)
  - χ̃⁰₁ stable (LSP)
- Output: HepMC3 ASCII (`sim/run_pythia8_001/events.hepmc`)

### 3. Detector simulation (Delphes 3, CMS card)

- Card: standard `delphes_card_CMS.tcl`
- Input: HepMC3 from Pythia8
- Output: `data/delphes_output.root` (50,000 events)

### 4. NLO cross section (Prospino 2.1)

- Process: `nn` (χ̃⁺₁ χ̃⁰₂), √s = 13 TeV, m = 550 GeV
- σ_NLO(χ̃⁺₁χ̃⁰₂) = 0.0198 pb, σ_LO = 0.0168 pb, K = 1.179
- Total NLO (both charge states) estimated as σ_LO(total) × K = 0.02028 × 1.179 = **0.02391 pb**

## Signal Region Cuts (VZ region, Table 1)

Applied in `analysis.py` / `analysis/analysis.py`:

1. **Lepton acceptance**: pT > 10 GeV, |η| < 2.4 (2.5 for e), exclude ECAL transition 1.4 < |η| < 1.6
2. **OCSF pair**: exactly 2 same-flavour (ee or μμ) leptons; leading pT > 25 GeV, subleading pT > 20 GeV, opposite charge, ΔR(ℓℓ) > 0.1
3. **Extra lepton veto**: events with any additional good lepton (pT > 10 GeV) rejected
4. **Z window**: 86 < m(ℓℓ) < 96 GeV
5. **Dilepton pT**: pT(ℓℓ) > 25 GeV
6. **MET pre-cut**: E_T^miss > 100 GeV
7. **Jets**: pT > 35 GeV, |η| < 2.4, ΔR > 0.4 from leptons; N_jets ≥ 2
8. **B-veto**: 0 b-tagged jets (CSV medium WP in Delphes CMS card)
9. **Δφ(jet, MET)**: Δφ(j₁, E_T^miss) > 0.4 and Δφ(j₂, E_T^miss) > 0.4 (two highest-pT jets)
10. **MT2(ℓℓ) > 80 GeV**: stransverse mass computed from two massless leptons and E_T^miss
11. **m_jj < 110 GeV**: invariant mass of the two jets with smallest |Δφ(j,j)|

## Cutflow (unweighted)

| Cut | Events surviving |
|---|---|
| Total generated | 50,000 |
| E_T^miss > 100 GeV | 43,692 |
| OCSF dilepton (Z window + pT(ll) + extra lep veto) | 881 |
| Njets ≥ 2, b-veto, Δφ(jet,MET) > 0.4 | 469 |
| MT2(ℓℓ) > 80 GeV + m_jj < 110 GeV | 239 |

Selection efficiency: 239/50000 = 0.478%

## Normalisation

weight per event = σ_NLO × L / N_gen = 0.02391 pb × 35,900 pb⁻¹ / 50,000 = 0.01717

## Deviations from Paper

1. **Detector simulation**: The paper uses a full GEANT4-based CMS simulation with detailed pileup modelling and fast simulation for signals. This analysis uses Delphes 3 with the generic CMS card, which provides approximate lepton/jet efficiencies and resolution smearing without pileup.

2. **NLO cross section**: The paper uses NLO+NLL cross sections from the LHC SUSY Cross Section Working Group. This analysis uses Prospino 2.1 NLO (no soft-gluon NLL resummation). The NLL correction at 550 GeV would increase the cross section by roughly 10–15%, potentially raising yields by the same amount.

3. **Charged-track lepton veto**: The paper also vetoes events with isolated charged-particle tracks (pT > 10 GeV for e/μ-like tracks, pT > 10 GeV for hadronic tracks). This is not modelled in Delphes.

4. **Trigger efficiency**: The paper applies trigger efficiency corrections of 90–96%. This analysis does not apply explicit trigger weights (effectively assumes 100% trigger efficiency).

5. **Lepton isolation**: The paper applies a mini-isolation criterion (shrinking cone ΔR = max(0.05, 10 GeV/pT) with |sum pT/pT| < 0.1 (0.2) for e (μ)). Delphes applies its own fixed-cone isolation criterion from the CMS card.

6. **χ̃⁰₂ decay coupling**: In the pure wino-bino MSSM, the χ̃⁰₂→Zχ̃⁰₁ coupling is exactly zero at tree level, requiring the production-only + Pythia8 decay approach described above. The paper likely uses a small admixture or a phenomenological rescaling; here we enforce 100% BR via Pythia8 DECAY blocks, which is physically equivalent for the simplified-model interpretation.

## Artifacts

| Artifact | Location |
|---|---|
| MadGraph5 process card | `sims/proc_card_prod_only.dat` |
| SLHA param card | `sims/TChiWZ_550_200.slha` |
| Pythia8 SLHA (with DECAY blocks) | `sims/TChiWZ_550_200_pythia.slha` |
| Delphes CMS card | `sim/run_delphes_001/delphes_card_CMS.tcl` |
| Pythia8 shower driver | `sim/shower.py` |
| Delphes output ROOT file | `data/delphes_output.root` |
| Analysis code | `analysis/analysis.py` |
| Histogram results | `results/histogram_TChiWZ.yaml` |
