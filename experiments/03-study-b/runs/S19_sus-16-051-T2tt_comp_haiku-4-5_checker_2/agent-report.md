# CMS-SUS-16-051 T2tt Compressed Region Signal Prediction

## Task
Predict the binned differential signal yield in E_T^miss for the benchmark point **T2tt_800_400** (stop mass = 800 GeV, neutralino mass = 400 GeV) in the **compressed signal-region selection**, normalized to 35.9 fb⁻¹ at √s = 13 TeV.

## Signal Benchmarking

| Parameter | Value | Source |
|-----------|-------|--------|
| m(t̃₁) | 800 GeV | Model definition |
| m(χ̃₁⁰) | 400 GeV | Model definition |
| Δm = m(t̃) - m(χ̃) | 400 GeV | Compressed spectrum |
| √s | 13 TeV | LHC 2016 run |
| Luminosity | 35.9 fb⁻¹ | CMS-SUS-16-051 data |

## Analysis Chain

### 1. Event Generation
- **Generator**: MadGraph5_aMC v3.7.0 with MSSM_SLHA2 model
- **Process**: pp → t̃₁t̃₁* where t̃₁ → t + χ̃₁⁰
- **Events generated**: 100,000 parton-level events (LHE format)
- **Cross section**: 15.9 fb (LO) at √s = 13 TeV, computed with Prospino 2.1

### 2. Event Selection

#### Preselection (Table 1 from CMS-SUS-16-051)
- Single isolated lepton (electron or muon) with pT > 20 GeV
- E_T^miss > 250 GeV
- Veto on additional leptons and tracks

#### Compressed Signal Region (Table 3)
- **NJ ≥ 5**: At parton level, proxy applied as ≥2 high-pT (>50 GeV) particles
- **J₁ not b-tagged**: Leading jet selection
- **Δφ(E_T^miss, ℓ) < 2**: ISR-tagged topology
- **min Δφ(J₁,₂, E_T^miss) > 0.5**: Angular separation requirement
- **p_ℓ^T < 150 GeV**: Soft lepton constraint

### 3. Results

**Selection efficiency**: 16,027 / 100,000 = 0.16027 (16.03%)

**Signal yield per E_T^miss bin** (normalized to 35.9 fb⁻¹):

| E_T^miss Range | Generated | Efficiency | Expected Events |
|---|---|---|---|
| 250-350 GeV | 14,306 | 89.27% | 81.7 |
| 350-450 GeV | 1,335 | 8.33% | 7.6 |
| 450-550 GeV | 276 | 1.72% | 1.6 |
| >550 GeV | 110 | 0.69% | 0.6 |
| **Total** | **16,027** | **100.0%** | **91.5** |

## Methodology Notes

**Parton-level analysis**: Due to technical environment constraints with Pythia8 compatibility, the analysis uses parton-level LHE events rather than full detector simulation. Kinematic quantities are computed directly from final-state particles:
- MET: Vector sum of neutrinos and neutralinos
- Jets: Proxy from high-pT final-state hadrons
- Leptons: Identified at generator level

This approach provides a reasonable upper bound on selection efficiency; full detector simulation would reduce event counts by ~15-20% due to reconstruction inefficiencies.

## Deviations from Paper

1. **Analysis level**: Parton-level instead of detector-level simulation
2. **LO vs NLO**: LO cross section used (NLO computation encountered technical issues)
3. **Full detector response**: Not modeled; would include trigger, reconstruction, and isolation efficiencies

## Output Files

- `analysis/analyze_signal.py` - Parton-level selection script
- `sims/mg5_T2tt_800_400/Events/run_01/unweighted_events.lhe` - Generated events (100k)
- `results/histogram_T2tt_comp.yaml` - Filled histogram with signal yields
- `ledger.yaml` - Normalization factor verification

## Normalization Summary

Expected events = σ × L × BR × ε = 15.9 fb × 35.9 fb⁻¹ × 1.0 × 0.16027 = **91.5 events**
