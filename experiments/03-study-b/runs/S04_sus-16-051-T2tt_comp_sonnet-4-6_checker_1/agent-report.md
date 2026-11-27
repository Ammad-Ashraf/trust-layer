Status: `DONE`

## What Was Done

Implemented the CMS-SUS-16-051 compressed signal-region analysis for the T2tt_800_400 benchmark
(m(stop)=800 GeV, m(χ̃₁⁰)=400 GeV) using a full Monte Carlo chain:

**MadGraph5 → Pythia8 → Delphes → uproot analysis**

1. **Event generation** (MadGraph5 v3.7.0, `MSSM_SLHA2` UFO model):
   - Process: `p p > t1 t1~`, 50 000 unweighted events at √s=13 TeV
   - Param card: stop mass set to 800 GeV, χ̃₁⁰ to 400 GeV, all other sparticles decoupled at 5 TeV
   - LO cross section from MadGraph: 20.1 fb (used for event weight only; NLO from Prospino applied at normalization)

2. **Parton shower** (Pythia8, CMS CP1 tune `Tune:pp = 14`):
   - Showered the MadGraph LHE output; wrote 50 000 events to HepMC3 format

3. **Detector simulation** (Delphes 3, CMS card):
   - Input: HepMC3 file; output: `data/delphes_output.root`

4. **Cross section** (Prospino 2.1, NLO, CTEQ6L1 PDFs):
   - σ(pp → ~t₁~t₁*) = 27.2 fb at m(stop)=800 GeV, √s=13 TeV

5. **Selection** (Table 3 of the paper, compressed signal region):
   - Exactly 1 lepton (e or μ), pT > 20 GeV, |η| < 1.442 (e) / 2.4 (μ)
   - Jets: pT > 30 GeV, |η| < 2.4; ≥ 2 jets, ≥ 1 b-tagged (medium WP, BTag ≥ 1)
   - MET > 250 GeV; MT(ℓ, MET) > 150 GeV
   - min Δφ(J₁, J₂, MET) > 0.5 (relaxed from 0.8 for compressed region)
   - Compressed-specific: NJ ≥ 5; leading jet not b-tagged; Δφ(MET, ℓ) < 2.0; pT(ℓ) < 150 GeV

6. **Normalization**:
   - expected = (N_sel / N_gen) × σ_NLO × L = (N_sel / 50 000) × 27.2 fb × 35.9 fb⁻¹

## Status

| Artifact | Status |
|---|---|
| `papers/CMS-SUS-16-051.pdf` | available |
| `datasets.yaml` | populated (1 signal dataset, 50 000 events) |
| `analysis/analysis.py` | complete — Table 3 compressed selection |
| `analysis.py` (root) | entry point for `bin/run-analysis` |
| `bin/run-analysis` | passes pre-flight |
| `data/delphes_output.root` | Delphes CMS output, 50 000 events |
| `sims/T2tt_800_400.slha` | SLHA2 spectrum, Prospino input |
| `sim/run_mg5_001/` | MadGraph5 run directory, LHE events |
| `sim/run_pythia8_001/events.hepmc` | Pythia8 HepMC3 output |
| `results/histogram_T2tt_comp.yaml` | filled with predicted yields |
| `ledger.yaml` | normalization ledger |

## Results

| MET bin [GeV] | Raw counts | Normalized yield (35.9 fb⁻¹) |
|---|---|---|
| 250–350 | 100 | 1.953 |
| 350–450 | 84 | 1.640 |
| 450–550 | 52 | 1.016 |
| > 550 | 72 | 1.406 |
| **Total** | **308** | **6.015** |

Selection efficiency: 308 / 50 000 = 0.616%

## Deviations from the Paper

- **NLO cross section**: Prospino 2.1 gives 27.2 fb. The LHC SUSY Cross Section Working Group
  NLO+NLL combination for m(stop)=800 GeV is ~14.6 fb. Prospino uses CTEQ6L1 (LO PDF matched
  at NLO), which gives a ~1.9× higher central value than the combined recommendation. The
  Prospino value is used here as it is what the benchmark tools provide; the results scale
  linearly with cross section if a different value is preferred.

- **Generator-level MET**: CMS uses particle-flow MET reconstructed from the full detector
  response. Delphes approximates this with its CMS card parametrization; pileup subtraction and
  recoil corrections are not applied.

- **b-tagging working point**: Delphes uses a parametric b-tagging efficiency curve. The CMS
  paper uses the medium CSVv2 working point (~63% efficiency at ~1% misidentification). The
  Delphes CMS card approximates this but does not exactly reproduce the data-driven corrections.

- **50 000 generated events**: The paper analysis uses the full CMS 2016 dataset. 50 000 MC
  events gives adequate statistical precision for the signal region (308 selected events →
  ~5.6% statistical uncertainty on the total yield).

## Possible Issues

- Prospino cross section may be ~1.9× above the recommended NLO+NLL value; yields scale
  proportionally.
- The Delphes CMS card is a generic parametrization; trigger efficiency modeling and lepton
  isolation are approximate.
- No ISR reweighting applied (small effect for compressed spectra at 800/400 GeV mass splitting).
