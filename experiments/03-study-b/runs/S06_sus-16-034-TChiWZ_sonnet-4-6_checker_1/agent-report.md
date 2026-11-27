Status: `DONE`

## What Was Done

Generated TChiWZ_550_200 signal events (pp → χ̃⁺₁χ̃⁰₂, m=550/550/200 GeV) and applied
the CMS-SUS-16-034 VZ electroweak signal region to obtain MET-binned expected yields
at 35.9 fb⁻¹.

### Simulation chain

1. **MadGraph5 3.7.0** (LO matrix elements, MSSM_SLHA2 model, 50k events)
   - Process: `pp > n2 x1+` and `pp > n2 x1-`
   - σ_LO(generator) = 18.37 fb (combined, NNPDF3.0, 13 TeV)
   - Sparticle masses set via `param_card`: m(χ̃⁺₁)=m(χ̃⁰₂)=550 GeV, m(χ̃⁰₁)=200 GeV, all others at 3 TeV

2. **Prospino 2.1** (NLO cross sections, CTEQ6, 13 TeV)
   - σ_NLO(pp→χ̃⁺₁χ̃⁰₂) = 8.52 fb (K=1.17)
   - σ_NLO(pp→χ̃⁻₁χ̃⁰₂) = 3.35 fb (K=1.23)
   - σ_NLO(total) = 11.87 fb

3. **Pythia8 8.313** (parton shower + hadronization, tune CP1)
   - Decays injected into LHE header: χ̃⁰₂→Z χ̃⁰₁ (100%), χ̃⁺₁→W⁺ χ̃⁰₁ (100%)
   - Z and W further decayed by Pythia8 according to SM branching fractions
   - 50k events → `sim/TChiWZ_550_200.hepmc` (2.8 GB HepMC3 Asciiv3)

4. **Delphes 3.x** (CMS detector simulation, `delphes_card_CMS.tcl`)
   - Run on first 10k HepMC events
   - Output: `data/TChiWZ_550_200.root` (10,000 events)

### Analysis (CMS-SUS-16-034 VZ signal region)

Cuts applied in `analysis/analysis.py`:
- 2 OSSF leptons (ee or μμ), leading pT>25, subleading pT>20 GeV, |η|<2.4/2.5
- Dilepton mass: 86 < m(ℓℓ) < 96 GeV (on-Z)
- Dilepton pT > 25 GeV, ΔR(ℓℓ) > 0.1
- ≥2 jets (pT>35, |η|<2.4), b-veto, Δφ(j1,j2, MET) > 0.4
- MT2(ℓℓ) > 80 GeV
- Closest-in-φ dijet mass < 110 GeV
- MET > 100 GeV, lepton veto (no extra pT>10 GeV leptons)

**Result:** 35 / 10,000 events pass all cuts (ε_sel = 0.35%)

### Expected yields

Normalization: N = σ_NLO × L × ε_bin = (11.87 fb) × (35.9 fb⁻¹) × (n_bin/10000)

| MET bin [GeV] | Raw counts | Expected yield |
|---|---|---|
| 100–150 | 3 | 0.128 |
| 150–250 | 8 | 0.341 |
| 250–350 | 15 | 0.639 |
| > 350   | 9 | 0.384 |
| **Total** | **35** | **1.49** |

## Status

| Artifact | Status |
|---|---|
| `papers/CMS-SUS-16-034.pdf` | ✓ read |
| `sims/TChiWZ_550_200.slha` | ✓ created |
| `sims/proc_card_TChiWZ.dat` | ✓ created |
| `sim/mg5_TChiWZ/Events/run_01/unweighted_events.lhe` | ✓ 50k events |
| `sim/TChiWZ_550_200.hepmc` | ✓ 50k events, 2.8 GB |
| `data/TChiWZ_550_200.root` | ✓ 10k Delphes events, 317 MB |
| `analysis/analysis.py` | ✓ VZ region cuts |
| `results/histogram_TChiWZ.yaml` | ✓ filled |
| `ledger.yaml` | ✓ all quantities recorded |
| `report.md` | ✓ this file |

## Possible Issues

- **Limited statistics**: Analysis uses 10k out of 50k generated events (memory constraint). MET bin [100-150] has only 3 raw events (58% statistical uncertainty). Bin [250-350] has the most events (15) with 26% uncertainty.
- **MHepMC3 vertex format**: pyhepmc 2.16.1 writes E-line nVertices=1 but Delphes's EventReady() requires fVertexCounter=-1 (needs 2 decrements from 1 vertex). Fixed by patching E-line to nVertices=0.
- **χ̃⁰₂ decay**: Original MG5 LHE had no BR lines in DECAY block; fixed by patching the LHE header SLHA section to include χ̃⁰₂→Z χ̃⁰₁ and χ̃⁺₁→W⁺ χ̃⁰₁ at 100% BR.
- **PDF mismatch**: MG5 LO (NNPDF, 18.37 fb) vs Prospino LO (CTEQ6, ~10 fb) differ by ~1.8×. Using Prospino NLO = 11.87 fb for final normalization.
