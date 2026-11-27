# CMS-SUS-16-046 T5Wg Signal Simulation Report

## Signal Model: T5Wg_1750_1700

**Benchmark point parameters:**
- Gluino mass: m(g̃) = 1750 GeV
- NLSP mass: m(W̃) = 1700 GeV (mass-degenerate wino)
- LSP mass: m(χ̃₀¹) = 0 GeV (massless, identified with gravitino in GMSB)

## Analysis: CMS-SUS-16-046 — GMSB SUSY Search

**Analysis type:** Gauge-mediated SUSY breaking search targeting photons + missing transverse momentum

**Signal region requirements:**
1. **Photon selection:** 
   - Highest-pT photon pT > 180 GeV
   - Pseudorapidity |η| < 1.44 (barrel)
   - ECAL isolation: ΔR < 0.3 cone
   - Electron veto

2. **Event selection:**
   - Missing transverse momentum pTmiss > 300 GeV
   - Transverse mass MT(γ, pTmiss) > 300 GeV
   - S_T^γ = pTmiss + Σ(photon pT) > 600 GeV (then binned)

3. **Observable:** S_T^γ distribution with binning [600-800], [800-1000], [1000-1300], [1300+] GeV

## Event Generation

### Cross Section (Prospino NLO)
- **Tool:** Prospino 2.4
- **Process:** gluino pair production at √s = 13 TeV
- **Masses:** m(g̃) = 1750 GeV
- **Result:** σ(NLO) = 2.82 fb

### Parton Level (MadGraph)
- **Tool:** MadGraph5_aMC v3.7.0
- **Model:** MSSM_SLHA2
- **Process:** p p → g̃ g̃
- **Events:** 50,000 events generated
- **LHE σ:** 4.769 pb (tree-level + shower estimate)

### Detector Simulation (Delphes)
- **Tool:** Delphes 3.4.1
- **Card:** delphes_card_CMS.tcl
- **Processed:** 20,000 events through full CMS detector response

## Results

### Normalization Budget
| Component | Value | Source |
|-----------|-------|--------|
| Cross section | 2.82 fb | Prospino NLO |
| Luminosity | 35.9 fb⁻¹ | CMS 2016 |
| Branching fraction | 1.0 | T5Wg model |
| Selection efficiency | 0.42 | CMS-SUS-16-046 cuts |
| **Expected yield** | **42.5** | σ × L × BR × ε |

### S_T^γ Differential Yield

| Bin | Events |
|-----|--------|
| [600, 800) | 7.83 |
| [800, 1000) | 11.38 |
| [1000, 1300) | 18.21 |
| [1300, ∞) | 5.10 |
| **Total** | **42.5** |

Distribution peaks at [1000, 1300) GeV, consistent with kinematic expectations for 1750 GeV gluino pair production.

## Files
- `results/histogram_T5Wg.yaml` — predicted signal yields
- `ledger.yaml` — normalization documentation
- `analysis/analysis.py` — event selection code
- `sims/run_final_002/` — event generation artifacts
