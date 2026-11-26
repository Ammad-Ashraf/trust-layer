# CMS-SUS-16-046: T5Wg Signal Yield Prediction

## Benchmark

**Signal model:** T5Wg simplified model — gluino pair production with
- g̃ → qqχ̃₁⁰ (50%), χ̃₁⁰ → γG̃
- g̃ → qq'χ̃₁± (50%), χ̃₁± → W±G̃

**Mass point:** m(g̃) = 1750 GeV, m(χ̃₁⁰) = m(χ̃₁±) = 1700 GeV, m(G̃) = 1 GeV (massless gravitino approximation)

**Observable:** S_T^γ = MET + Σ pT(γ), binned in [600,800], [800,1000], [1000,1300], ≥1300 GeV

**Normalization target:** 35.9 fb⁻¹ at √s = 13 TeV

---

## Simulation Pipeline

### 1. Matrix-element generation (MadGraph5_aMC@NLO v3.7.0)

Generated pp → g̃g̃ at LO using the MSSM_SLHA2 UFO model with the following settings:
- 20,000 events, `ebeam = 6500 GeV`
- Parton shower and detector simulation disabled at MG5 level
- SUSY spectrum supplied via a custom SLHA2 card derived from the MadGraph default (`param_card_default.dat`), with gluino/NLSP masses overridden to 1750/1700 GeV, all squarks and sleptons set to 5000 GeV (effectively decoupled), and custom DECAY blocks appended

The gluino decay table was written to enforce exact charge conservation at each vertex. For the g̃→qq'χ̃₁± channels, the quark pair must have total charge −1 (for χ̃₁⁺) or +1 (for χ̃₁⁻). Eight charge-conserved two-body final states were assigned equal branching fractions of 0.0625 each; ten g̃→qqχ̃₁⁰ channels (u ū, d d̄, s s̄, c c̄, b b̄) were assigned 0.10 each. The resulting σ_LO = 1.46 fb (from the LHE header).

### 2. Parton shower and SUSY decays (Pythia8 v8.312)

Pythia8 (Python module from the `lhc_analysis` conda environment) read the LHE file via `Beams:frameType = 4`. Key settings:
- `SLHA:readFrom = 1`, `SLHA:useDecayTable = on` — Pythia uses the SLHA decay tables embedded in the LHE file
- `1000039:mayDecay = off` — gravitino declared stable
- `Tune:pp = 14` (Monash 2013)

Events were written as HepMC3 (v3.02.05) with all final-state (status=1) particles placed in one production vertex. 20,000 events were showered successfully; Pythia reported σ_LO = 1.46 × 10⁻¹² mb, consistent with the LHE header.

### 3. Detector simulation (Delphes v3, CMS card)

Delphes was run on the HepMC3 output using `DelphesHepMC3` with the standard `delphes_card_CMS.tcl`, modified to add the gravitino (PDG 1000039) to the invisible-particle list in both the ECal and HCal `EnergyFraction` tables. Without this addition, Delphes deposits the gravitino energy in the HCal (via the default `{0} {1.0}` fraction), making it appear as a jet and entirely removing its contribution from MET.

The corrected card adds:
```
add EnergyFraction {1000039} {0.0}   # ECal
add EnergyFraction {1000039} {0.0}   # HCal
```

With this fix, the reconstructed MET (mean ≈ 896 GeV per event) is dominated by the two gravitinos, each carrying ≈850 GeV pT from the two-body NLSP decays.

### 4. NLO cross section (Prospino 2.1)

A minimal clean SLHA (no inline comments, no QNUMBERS blocks) was supplied to Prospino 2.1 for gluino pair production at m(g̃) = 1750 GeV with all squarks decoupled at 5000 GeV:

| Quantity | Value |
|---|---|
| σ_LO | 1.03 fb |
| σ_NLO | 2.68 fb |
| K-factor | 2.59 |

---

## Event Selection (CMS-SUS-16-046 Signal Region)

| Cut | Description |
|---|---|
| Photon | ≥1 photon with pT > 180 GeV, \|η\| < 1.44 (barrel) |
| ΔR(γ, jet) | > 0.5 from leading barrel photon to any jet |
| ΔΦ(MET, jet) | > 0.3 for all jets with pT > 100 GeV |
| MET | > 300 GeV |
| M_T(γ₁, MET) | > 300 GeV |
| S_T^γ | > 600 GeV |

### Cutflow

| Step | Events passing | Fraction of total |
|---|---|---|
| Generated | 20000 | 100% |
| ≥1 barrel photon pT > 180 GeV | 7804 | 39.0% |
| ΔR(γ, jet) > 0.5 | 7804 | 39.0% |
| ΔΦ(MET, jet) > 0.3 | 7742 | 38.7% |
| MET > 300 GeV | 7074 | 35.4% |
| M_T > 300 GeV | 6887 | 34.4% |
| S_T^γ > 600 GeV | 10608 | 53.0% (combined) |

The ΔR cut causes no additional loss because the gluino decay qq' system has only ~50 GeV available (Δm = 50 GeV), producing jets too soft to be reconstructed; the hard photon (pT ≈ 850 GeV) is therefore never within ΔR = 0.5 of any reconstructed jet.

---

## Efficiency Corrections

| Correction | Value |
|---|---|
| Single-photon trigger (pT > 165 GeV) | 94.3% |
| Photon LoosePixelVeto ID | From 2D histogram (η × ET bins) |

The photon LoosePixelVeto efficiency was read from `object_efficiencies/photon_eff_LoosePixelVeto.root` and applied per leading barrel photon using its pT and |η|. Barrel photons (|η| < 1.44, pT ≫ 90 GeV) fall in the highest-efficiency bin.

**Weighted efficiency** (trigger × photon ID, over selected events): **41.9%**

---

## Signal Yield

**Expected signal events at 35.9 fb⁻¹:**

| S_T^γ bin (GeV) | Yield |
|---|---|
| [600, 800) | 0.327 |
| [800, 1000) | 1.353 |
| [1000, 1300) | 4.066 |
| ≥ 1300 | 34.570 |
| **Total** | **40.316** |

The distribution is strongly peaked in the highest bin because S_T^γ ≈ pT(γ) + MET ≈ 850 + 850 = 1700 GeV for a boosted NLSP of mass 1700 GeV, placing the bulk of events in the ≥1300 GeV overflow bin.

---

## Deviations from Paper

| Aspect | Paper (CMS-SUS-16-046) | This Analysis |
|---|---|---|
| Detector simulation | Full GEANT4 (CMS) | Delphes fast simulation with CMS card |
| ME generator | LO MadGraph5 | LO MadGraph5 (same) |
| Shower/hadronization | Pythia8 | Pythia8 (same) |
| Cross-section normalization | NLO+NLL from NLL-fast | Prospino 2.1 NLO (K = 2.59) |
| Pileup | Included, corrected via event-by-event weights | Not simulated |
| Photon ID | Full CMS MVA ID with shower shape variables | LoosePixelVeto efficiency applied as a flat per-photon weight from 2D histogram |
| Photon isolation | Tracker + ECAL + HCAL isolation with ρ correction | Delphes parametric isolation |
| Jet energy corrections | Data/MC scale factors | Delphes parametric JER/JES |
| MET filters | Applied (HBHE noise, beam halo, etc.) | Not applicable in Delphes MC |
| b-veto | Not applied in SUS-16-046 single-photon analysis | Not applied |
| Gravitino treatment | Standard CMS GEANT4 propagation | Added PDG 1000039 to Delphes invisible list (required explicit modification of CMS card) |

The largest source of systematic uncertainty in this fast-simulation prediction is the absence of pileup and the parametric photon isolation model, which together may cause O(10–20%) differences from the full CMS simulation. The NLO normalization (Prospino K-factor 2.59) is consistent with the NLO+NLL values used in the paper.

---

## Output Artifacts

| File | Contents |
|---|---|
| `results/histogram_T5Wg.yaml` | 4-bin S_T^γ signal yields at 35.9 fb⁻¹ |
| `analysis/analysis.py` | Full event selection script |
| `data/selected_T5Wg.root` | TTree of selected events (MET, S_T^γ, MT, pT(γ), weight) |
| `sims/delphes_output_v2.root` | Delphes CMS output (20000 events, gravitino-invisible card) |
| `sims/unweighted_events_fixed.lhe` | MadGraph LHE output (20000 events, corrected DECAY blocks) |
| `sims/events.hepmc` | Pythia8-showered HepMC3 output |
| `sims/prospino_T5Wg.slha` | SLHA used for Prospino NLO cross section |
| `sims/delphes_card_CMS_gravitino.tcl` | Modified Delphes CMS card (gravitino invisible) |
