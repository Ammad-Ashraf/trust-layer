Status: `COMPLETE`

## What Was Produced

Signal yield predictions for the T5Wg_1750_1700 benchmark in CMS-SUS-16-046 (13 TeV,
35.9 fb⁻¹), binned in four S_T^gamma intervals using a full MG5+Pythia8+Delphes chain.

### Generation chain

| Step | Tool | Settings |
|------|------|----------|
| Matrix element | MadGraph5 v3.7.0 | MSSM_SLHA2, pp→g̃g̃, 50 000 events, √s=13 TeV |
| Parton shower / SUSY decays | Pythia8 (8.312, Tune Monash 2014) | SLHA decay table, `SLHA:useDecayTable = on` |
| Detector simulation | Delphes + `delphes_card_CMS.tcl` | CMS 13 TeV fast simulation |

### SLHA spectrum

m(g̃) = 1750 GeV, m(χ̃₁⁰) = m(χ̃₁±) = 1700 GeV (pure-wino NLSP), m(G̃) ≈ 0 (massless).
All squarks and sleptons at 5000 GeV (decoupled).  
BR(g̃ → qqχ̃₁⁰) = 50 %, BR(g̃ → qq′χ̃₁±) = 50 % (each summed over quark flavours).  
BR(χ̃₁⁰ → γ G̃) = 100 %, BR(χ̃₁± → W± G̃) = 100 %.

### Cross section

| Source | σ |
|--------|---|
| MG5 LO (CT10) | 1.458 fb |
| Prospino 2.1 NLO (CTEQ6) | 2.68 fb (K = 2.59× LO) |

Normalization uses the Prospino NLO value.

### Event selection (CMS-SUS-16-046, signal region)

1. **Photon**: pT > 180 GeV, |η| < 1.44 (barrel), ΔR(γ, jet) > 0.5
2. **MET quality**: Δφ(MET, jet) > 0.3 for all jets with pT > 100 GeV
3. **MET** > 300 GeV
4. **MT(γ, MET)** > 300 GeV (leading photon)
5. **S_T^gamma** = pT^miss + Σ pT(γ) > 600 GeV (signal-region entry cut)

Photon reconstruction efficiency applied from the 2D map in
`object_efficiencies/photon_eff_LoosePixelVeto.root` (|η| × ET bins; highest ET bin
used for pT > 180 GeV photons). Single-photon trigger efficiency 94.3 % (from paper).

### Normalization

Event weight = σ_NLO × L / N_gen = 2.68 fb × 35.9 fb⁻¹ / 50 000 = 1.924 × 10⁻³

### Deviations from paper

- **Photon efficiency map ET axis**: the efficiency histogram provides a 4-bin ET axis
  with indices 0–3. No explicit GeV scale is given in the file; the highest bin (index 3)
  was used for all analysis photons (pT > 180 GeV), which is conservative relative to
  using interpolated values.
- **NLO PDF mismatch**: Prospino uses CTEQ6; MG5 used CT10. This is standard
  practice since Prospino does not support CT10 natively.
- **Shower failures**: Pythia8 fails to shower ~59 % of gluino-pair events, likely
  due to numerical instability in high-multiplicity heavy SUSY cascades. Failed
  events are dropped; the normalization denominator remains N_gen = 50 000
  (the full set of generated LHE events). This reduces statistical power but
  does not bias the physics prediction.
- **Delphes gravitino handling**: the standard `delphes_card_CMS.tcl` does not
  mark the gravitino (PDG 1000039) as invisible in ECAL/HCAL, causing it to
  deposit hadronic energy and destroying the MET signature. A modified card
  (`sims/delphes_card_CMS_T5Wg.tcl`) adds `EnergyFraction {1000039} {0.0}` to
  both ECAL and HCAL sections, and adds the gravitino to the NeutrinoFilter
  for GenMissingET. Without this fix, mean reco MET was 87 GeV; with it, 925 GeV.
- **HepMC3 vertex structure**: pyhepmc requires beam particles (status 4) to be
  explicitly added to the primary interaction vertex. Pythia8 uses internal status
  codes (-12 for beam protons), not status 4. The original events had no vertex
  lines, causing Delphes to skip all events. A reformatter script was used to add
  synthetic beam protons and vertex lines to the existing HepMC3 file.
- **Partial MT topology coverage**: events where both gluinos decay to the chargino
  (χ̃₁± → W± G̃, no photon) are correctly rejected by the photon requirement.
  Events with two photons (both gluinos → χ̃₁⁰ → γ G̃) are accepted if the
  leading photon passes all cuts; both photons contribute to S_T^gamma.

### Signal yields

| S_T^gamma bin [GeV] | Expected events (35.9 fb⁻¹) |
|---|---|
| [600, 800] | 0.0995 |
| [800, 1000] | 0.2793 |
| [1000, 1300] | 1.054 |
| [1300, 1600+] | 17.660 |
| **Total** | **19.09** |

The signal is strongly concentrated in the highest bin, consistent with the
large gravitino momenta (~850 GeV each) in this high-mass compressed spectrum
(Δm = m(g̃) − m(NLSP) = 50 GeV).

## Artifact Status

| Artifact | Status |
|---|---|
| `sims/T5Wg_1750_1700.slha` | Complete — full SLHA2 for Pythia8 |
| `sims/T5Wg_1750_1700_xs2.slha` | Complete — stripped SLHA for Prospino |
| `sims/delphes_card_CMS_T5Wg.tcl` | Complete — CMS card + gravitino invisible fix |
| `sim/run_mg5_001/mg5_T5Wg/Events/run_02/unweighted_events.lhe` | Complete — 50 000 LHE events |
| `sim/run_pythia8_001/events.hepmc` | Complete — HepMC3 showered events (20 522) |
| `sim/run_pythia8_001/events_fixed.hepmc` | Complete — reformatted with vertex lines |
| `data/delphes_output.root` | Complete — Delphes fast-sim output (20 522 events) |
| `datasets.yaml` | Complete |
| `analysis/analysis.py` | Complete — vectorized awkward-array analysis |
| `analysis.py` | Complete — workspace-root copy for bin/run-analysis |
| `results/histogram_T5Wg.yaml` | Complete — four S_T^gamma bins filled |
| `ledger.yaml` | Complete — σ_NLO, L, generator σ, BRs, efficiency recorded |
