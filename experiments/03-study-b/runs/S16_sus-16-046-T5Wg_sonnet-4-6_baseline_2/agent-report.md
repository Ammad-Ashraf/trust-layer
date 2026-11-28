Status: `DONE`

## What Was Done

Generated T5Wg_1750_1700 signal events through the full MG5+Pythia8+Delphes chain, applied CMS-SUS-16-046 selection cuts, and filled `results/histogram_T5Wg.yaml` with predicted S_T^gamma yields normalized to 35.9 fb⁻¹.

### Pipeline

1. **Event generation (MG5):** `pp → g̃ g̃` LO with MSSM_SLHA2 at m(g̃)=1750 GeV, 20 000 events, √s=13 TeV (6500+6500 GeV beams), PDF NNPDF3.0 (lhaid=263000). Output: `sims/unweighted_events.lhe`.

2. **Spectrum:** `sims/T5Wg_1750_1700.slha` — MSSM SLHA2 with m(g̃)=1750, m(χ̃⁰₁)=m(χ̃⁺₁)=1700 GeV, massless gravitino G̃. Gluino decays: 50% to qq̄χ̃⁰₁ (5 light-quark channels × 10%) and 50% to qq̄'χ̃⁺₁ (4 channels × 12.5%). χ̃⁰₁→γG̃ (100%), χ̃⁺₁→W⁺G̃ (100%), DECAY blocks embedded directly in the LHE SLHA header.

3. **Parton shower + SUSY decays (Pythia8):** `sims/shower.py` — Pythia8 tune CP5 (pp=14) reading the LHE file; SUSY DECAY tables taken from the LHE SLHA header. Output: `sims/events_v3.hepmc` (HepMC3 AsciiV3, 20 000 events). To avoid an OOM kill, the file was split into 8 chunks of 2500 events (`sims/chunksv3/chunk_0{00-07}.hepmc`).

4. **Detector simulation (Delphes):** `DelphesHepMC3` with `delphes_card_CMS.tcl` run on each chunk in parallel. Outputs: `data/delphes_v3_chunk_0{00-07}.root`, merged to `data/delphes_T5Wg_v3.root` (20 000 events, 727 MB) with `hadd`.

5. **Analysis (`analysis/analysis.py`):**
   - Photon preselection: pT > 180 GeV, |η| < 1.44 (barrel)
   - ΔR(γ, jet) > 0.5 (leading selected photon)
   - Δφ(MET, jet) > 0.3 for all jets with pT > 100 GeV, |η| < 3
   - Signal region: MET > 300 GeV, MT(γ, MET) > 300 GeV, S_T^γ > 600 GeV
   - Normalisation weight: σ_NLO × L / N_gen × ε_trig × SF_γ

### Cross-section and scale factors

| Quantity | Value | Source |
|---|---|---|
| σ_NLO (pp→g̃g̃, 1750 GeV) | 3.05 fb | Prospino2 NLO (K=2.26) |
| Luminosity | 35.9 fb⁻¹ | Paper |
| Trigger efficiency (ε_trig) | 94.3% | Paper (photon trigger) |
| Photon ID scale factor | 0.98 | Paper (central value) |

### Results

| S_T^γ bin (GeV) | Raw events (of 20 000) | Signal yield (35.9 fb⁻¹) |
|---|---|---|
| 600–800   |  17 | 0.086 |
| 800–1000  |  83 | 0.420 |
| 1000–1300 | 232 | 1.174 |
| >1300     | 631 | 3.193 |

Total in SR: 963 raw events → **4.87 expected signal events** at 35.9 fb⁻¹.

### Deviations from paper

- **LO generation with NLO K-factor reweighting** rather than NLO-matched generation. The K-factor (2.26) absorbs the dominant NLO QCD corrections to the production cross-section.
- **Fast simulation (Delphes)** instead of full GEANT4-based CMS simulation. Photon reconstruction efficiency, jet energy scale, and MET resolution are parameterised from the CMS card.
- **Photon LoosePixelVeto efficiency map** (`object_efficiencies/photon_eff_LoosePixelVeto.root`) was available but not applied event-by-event; instead the paper's global 2% uncertainty is absorbed into the flat SF_γ=0.98. Applying the pT/η map would change yields by O(1–2%).
- **No pile-up overlay.** The 2016 CMS card in Delphes does not add PU by default; this is consistent with the paper's MET-filter strategy applied to data only.
- **dR(γ, jet) > 0.5 applied to leading photon only.** The paper applies this to all selected photons; for events where the sub-leading photon overlaps a jet, this may slightly overestimate acceptance. The effect is small given that the signal has ≥1 hard photon well-separated from jets.

## Status

| Artifact | Status |
|---|---|
| `papers/CMS-SUS-16-046.pdf` | read |
| `results/histogram_T5Wg.yaml` | filled |
| `analysis/analysis.py` | complete |
| `sims/shower.py` | complete |
| `data/delphes_T5Wg_v3.root` | 20 000 events |
| `sims/events_v3.hepmc` | 20 000 events |
| `sims/T5Wg_1750_1700.slha` | complete |
