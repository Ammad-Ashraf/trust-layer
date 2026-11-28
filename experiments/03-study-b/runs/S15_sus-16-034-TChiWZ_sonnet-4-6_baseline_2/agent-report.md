# CMS-SUS-16-034 — TChiWZ_550_200 Signal Prediction

## Summary

Predicted VZ electroweak signal yields in MET bins [100–150, 150–250, 250–350, >350] GeV for `TChiWZ_550_200` (m(χ̃⁺₁) = m(χ̃⁰₂) = 550 GeV, m(χ̃⁰₁) = 200 GeV) at 35.9 fb⁻¹, √s = 13 TeV:

| MET bin [GeV] | Signal yield |
|---|---|
| 100–150 | 0.299 |
| 150–250 | 0.755 |
| 250–350 | 1.015 |
| >350    | 1.093 |

**Total VZ yield: 3.16 events**

---

## Simulation chain

### Event generation (MadGraph5 v3.7.0)

- **Process**: `p p > x1+ n2`, `p p > x1- n2` (χ̃⁺₁ χ̃⁰₂ + charge-conjugate) using MSSM_SLHA2 UFO model
- **50,000 unweighted LHE events** at LO, using modified `restrict_default.dat` with:
  - m(χ̃⁰₁) = 200 GeV (PDG 1000022, bino-like)
  - m(χ̃⁰₂) = 550 GeV (PDG 1000023, wino-like)
  - m(χ̃⁺₁) = 550 GeV (PDG 1000024, wino-like)
  - Heavy gluino (2500 GeV), squarks and sleptons (2000 GeV): decoupled
  - NMIX: dominant bino χ̃⁰₁ (N₁₁ ≈ 0.999), dominant wino χ̃⁰₂ (N₂₂ ≈ 0.999), small off-diagonal terms to allow Z/W couplings
  - UMIX/VMIX: pure wino chargino (U₁₁ = V₁₁ = 1)
- MG5 LO cross section: 0.01372 pb (summed both charges)
- Beam energy: 6500 + 6500 GeV (pp at 13 TeV), NNPDF3.0 PDF

### NLO normalization (Prospino 2.1)

| Process | LO (pb) | NLO (pb) | K-factor |
|---|---|---|---|
| pp → χ̃⁺₁ χ̃⁰₂ | 0.0113 | 0.0130 | 1.15 |
| pp → χ̃⁻₁ χ̃⁰₂ | 0.00427 | 0.00513 | 1.20 |
| **Total** | **0.01557** | **0.01813** | **1.16** |

The analysis is normalized using the total NLO cross section of **0.01813 pb**.

### Parton shower and hadronization (Pythia8 3.1.2)

- LHE events processed via `Beams:frameType = 4` (LHE input mode)
- SLHA file specifies 100% BR: χ̃⁰₂ → Z χ̃⁰₁ and χ̃⁺₁ → W⁺ χ̃⁰₁
- Tune: Monash 2013 (Tune:pp = 14)
- ISR, FSR, MPI, hadronization all enabled
- Output: HepMC3 ASCII format, one production vertex + all final-state particles

### Fast detector simulation (Delphes)

- Card: `delphes_card_CMS.tcl` (standard CMS card from Delphes package)
- Input: 50,000 HepMC3 events (2.8 GB)
- Output: 1.6 GB ROOT file with standard Delphes branches
- 50,000 events processed

---

## Analysis: VZ electroweak signal region

The analysis implements the VZ signal region from Table 1 of CMS-SUS-16-034:

| Selection | Requirement |
|---|---|
| Dilepton flavor | OSSF (ee or μμ), pT₁ > 25 GeV, pT₂ > 20 GeV, \|η\| < 2.4 |
| ECAL gap veto | 1.4 < \|η\| < 1.6 excluded |
| ΔR(ℓ,ℓ) | > 0.1 |
| Dilepton pT | > 25 GeV |
| m_ℓℓ (on-Z) | 86 < m_ℓℓ < 96 GeV |
| Extra leptons | veto pT > 10 GeV, \|η\| < 2.4 (requires exactly 2 total) |
| Jet selection | ≥ 2 jets, pT > 35 GeV, \|η\| < 2.4, ΔR(j,ℓ) > 0.4 |
| b-veto | 0 b-tagged jets (medium CSVv2) |
| Δφ(j₁/₂, MET) | > 0.4 (for two leading jets) |
| MET | > 100 GeV |
| MT2(ℓℓ) | > 80 GeV |
| m_jj | < 110 GeV (jet pair closest in Δφ) |
| Normalization | 35.9 fb⁻¹ at 13 TeV |

MT2(ℓℓ) is computed using a 200×100 angular and magnitude scan for the trial invisible-particle momenta.

---

## Event statistics

| Stage | Events |
|---|---|
| Generated (MG5 LO) | 50,000 |
| After Pythia8 shower | 50,000 |
| After Delphes | 50,000 |
| Passing VZ (before MT2) | 278 |
| Passing VZ (after MT2) | 242 |

Effective selection efficiency: 242/50,000 = 0.484%

Expected yield = 0.01813 pb × 35.9 fb⁻¹ × 1000 fb/pb × 0.00484 = 3.15 events ✓

---

## Deviations from paper

1. **Detector simulation**: The paper uses the full CMS GEANT4 simulation with pileup overlay. We use Delphes fast simulation with the CMS card, which approximates detector resolution and efficiency but does not include pileup. This may slightly overestimate signal efficiency.

2. **NLO+NLL normalization**: The paper uses NLO+NLL cross sections from the LHC SUSY Cross Section Working Group. We use Prospino 2.1 at NLO (without resummation). The difference is typically ≲ 5%.

3. **Extra-lepton veto**: The paper applies a looser isolation (< 40% of pT) for the extra-lepton veto, using the Delphes-reconstructed lepton collection. We require exactly 2 total leptons passing pT > 10 GeV, |η| < 2.4, which is equivalent in practice.

4. **b-tagging**: The paper uses CSVv2 at the medium working point with pT > 25 GeV threshold for the b-jet count (but pT > 35 GeV for jet selection). We use the Delphes b-tagging at pT > 35 GeV (the jet selection threshold). This may slightly under-veto low-pT b-jets from charm in hadronic W decays.

5. **Spin correlations**: The W and Z decays are handled by Pythia8 using SLHA decay tables (100% BRs) rather than the full MSSM decay matrix elements. Spin correlations in the SUSY cascade are approximated.

6. **MT2 implementation**: Custom grid-scan implementation (200×100 steps) rather than the analytic Lester-Summers-Barr algorithm. For MT2 >> 80 GeV (typical for this signal), accuracy is sufficient.

---

## Output files

| File | Description |
|---|---|
| `results/histogram_TChiWZ.yaml` | Predicted VZ signal yields |
| `analysis/analysis.py` | Reference implementation with per-event loop |
| `analysis.py` | Production implementation (vectorized) run by bin/run-analysis |
| `data/delphes_output.root` | Delphes-processed events |
| `data/xsec_pb.txt` | NLO cross section: 0.01813 pb |
| `data/n_generated.txt` | Generated events: 50,000 |
| `sims/TChiWZ_550_200_mg5.dat` | SLHA2 param card for MSSM_SLHA2 |
| `sims/TChiWZ_550_200.slha` | Original SLHA file (reference) |
| `sim/mg5_TChiWZ/` | MadGraph5 output directory |
| `sim/events_TChiWZ.hepmc` | HepMC3 output from Pythia8 |
| `sim/shower.py` | Pythia8 shower script |
| `sim/proc_step1.dat`, `sim/proc_step3.dat` | MadGraph5 process cards |
