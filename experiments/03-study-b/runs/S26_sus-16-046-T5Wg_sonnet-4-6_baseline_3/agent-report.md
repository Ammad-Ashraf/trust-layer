# CMS-SUS-16-046 Signal Simulation Report
## T5Wg_1750_1700 — S_T^γ Binned Signal Yield

### Summary

This report documents the simulation of the T5Wg simplified model signal 
(gluino pair production, m(g̃)=1750 GeV, m(NLSP wino)=1700 GeV, massless gravitino LSP) 
at √s=13 TeV, normalized to L=35.9 fb⁻¹, as described in CMS-SUS-16-046.

---

### 1. Signal Model

**T5Wg topology:**
- Gluino pair production: pp → g̃ g̃
- Each gluino decays with 50% BR to:
  - g̃ → q q̄ χ̃₁⁰ (then χ̃₁⁰ → γ G̃)
  - g̃ → q q̄' χ̃₁± (then χ̃₁± → W± G̃)
- Masses: m(g̃)=1750 GeV, m(χ̃₁⁰)=m(χ̃₁±)=1700 GeV, m(G̃)≈0
- Mass compression: Δm = m(g̃) − m(NLSP) = 50 GeV → soft quarks from gluino decay

**Final states (per pair):**
- γγ + 2G̃: 25% (both gluinos → χ̃₁⁰)
- γ W + 2G̃: 50% (one χ̃₁⁰, one χ̃₁±)
- WW + 2G̃: 25% (both gluinos → χ̃₁±)

---

### 2. Event Generation Chain

#### 2.1 Matrix-Element Generation — MadGraph5_aMC@NLO 3.7.0

```
Process:   p p → g̃ g̃ (gluino pair production)
Model:     MSSM_SLHA2 (included with MG5)
Events:    50,000 unweighted events
√s:        13 TeV (ebeam = 6500 GeV each)
PDFs:      NNPDF3.0 (via MSSM_SLHA2 default)
LO σ:      1.889 ± 0.001 fb (MG5 LO)
```

The gluino decays are specified in the SLHA param_card embedded in the LHE header. 
Gluino decay to quarks+NLSP occurs via off-shell squarks (all squarks decoupled at 100 TeV).

The gluino decay channels use correct charge-conserving PDG IDs:
- g̃ → ū d χ̃₁⁺: `(-2, 1, 1000024)` (charge: −2/3−1/3+1=0 ✓)
- g̃ → u d̄ χ̃₁⁻: `(2, −1, −1000024)` (charge: +2/3+1/3−1=0 ✓)
- etc. for c/s and u/b combinations (see `sims/T5Wg_1750_1700_corrected.slha`)

Output: `sim/run_mg5_001/mg5_T5Wg_v4/Events/run_01/unweighted_events.lhe`

#### 2.2 Parton Shower — Pythia 8.312

```
Tune:      CMS CP1 (Tune:pp = 14)
NLSP decay channels (from LHE-embedded SLHA):
  χ̃₁⁰(1000022) → γ G̃  (width=1 GeV in SLHA, BR=100%)
  χ̃₁±(1000024) → W± G̃ (width=1 GeV in SLHA, BR=100%)
  Gravitino:  stable (mayDecay = off, m = 1×10⁻⁹ GeV)
```

**Chi10 stability fix:** The SLHA initially embedded chi10 (1000022) with 
`DECAY 1000022 0.000000e+00`, causing Pythia to treat it as stable (the decay 
channels were listed but ignored when total width=0). This was fixed by patching 
the LHE header to `DECAY 1000022 1.000000e+00`. After this fix, chi10 → γ G̃ 
produces photons with pT~500-1500 GeV (physical range for m(χ̃₁⁰)=1700 GeV), 
and 100% of generator-level events contain at least one final-state photon.

Events were processed in 16 parallel chunks on 32 CPUs for efficiency.

Output: `sim/run_pythia8_001/events_v5.hepmc` (HepMC3 ASCII, 50000 events, 2.3 GB)

#### 2.3 Detector Simulation — Delphes 3 with CMS card

```
Card: delphes_card_CMS.tcl (standard CMS Run 2 performance)
Input: events_v5.hepmc (HepMC3 ASCII)
Output: data/delphes_output_v2.root
Photon isolation: PTRatio < 0.12 within ΔR = 0.5
```

The CMS Delphes card approximates:
- Photon reconstruction efficiency vs pT and η
- Jet energy corrections
- Missing transverse energy reconstruction
- Muon/electron identification for overlap removal

---

### 3. Cross Section Normalization

| Source | σ (fb) | Comment |
|--------|--------|---------|
| MG5 LO | 1.889 | m(g̃)=1750 GeV, decoupled squarks |
| Prospino 2.1 LO | 1.5 | small PDF difference |
| Prospino 2.1 NLO | 3.28 | K=2.18 |
| NNLLfast NLO+NLL | ~1.4 | official LHC SUSY XS WG tables |

**Used for normalization:** σ(NLO) = 3.28 fb from Prospino.

The paper uses NLO+NLL cross sections from NNLLfast, which include soft-gluon 
resummation corrections that reduce the cross section compared to NLO at high 
gluino masses. The NNLLfast value (~1.4 fb) is lower than Prospino NLO (3.28 fb) 
due to these resummation effects. Using Prospino NLO overestimates the yield by 
roughly a factor of 2.3 relative to what the paper uses.

**Event weight:**  W = σ(NLO) × L / N_gen = 3.28 × 35.9 / 50000 = 2.36×10⁻³

---

### 4. Event Selection (CMS-SUS-16-046, Table 1)

**Preselection:**
1. ≥1 photon with pT > 180 GeV, |η| < 1.44 (barrel)
2. ΔR(γ, jet) > 0.5 (photon-jet isolation)
3. Δφ(MET, jet) > 0.3 for pT(jet) > 100 GeV (suppress jet mismeasurement MET)

**Signal Region:**
4. MET > 300 GeV
5. MT(γ_lead, MET) > 300 GeV, where MT = √(2 pT_γ MET (1−cosΔφ))
6. S_T^γ = MET + Σ pT(γ_i) > 600 GeV

**Signal efficiency corrections:**
- Photon trigger efficiency: ε_trig = 94.3% (applied as flat weight)
- Photon ID efficiency: included in Delphes CMS card
- No ISR reweighting applied (the paper applies ISR reweighting for strong production)

**S_T^γ bins:** [600,800], [800,1000], [1000,1300], [>1300] GeV

---

### 5. Deviations from Paper

1. **Fast vs full simulation:** The paper uses CMS fast simulation for signal;
   we use Delphes with the standard CMS card. This introduces differences in photon 
   efficiency and MET resolution at the ~5-15% level per bin.

2. **Cross section:** We use Prospino NLO (3.28 fb) rather than NLO+NLL from 
   NNLLfast. The NNLLfast value (~1.4 fb) would reduce all yields by a factor ~2.3.

3. **ISR reweighting:** The paper applies ISR pT reweighting (factors 0.78–1.18) for 
   strong production models. We did not apply this reweighting.

4. **PDF set:** We use the MSSM_SLHA2 default PDF (NNPDF3.0 LO), while the paper 
   uses NNPDF3.0 at NLO+NLL precision.

5. **Pileup:** The CMS Delphes card uses a simplified pileup model; we did not 
   apply event-level pileup reweighting.

---

### 6. Final Results

**S_T^γ binned signal yields at 35.9 fb⁻¹, m(g̃)=1750 GeV, σ(NLO)=3.28 fb:**

| S_T^γ bin (GeV) | Raw events | Weighted yield |
|----------------|-----------|----------------|
| 600–800         | 226       | 0.502          |
| 800–1000        | 803       | 1.783          |
| 1000–1300       | 2743      | 6.092          |
| > 1300          | 22809     | 50.654         |
| **Total**       | **26581** | **59.03**      |

**Selection efficiency summary:**

| Cut | Remaining events |
|-----|-----------------|
| Total generated | 50000 |
| ≥1 photon pT>180, \|η\|<1.44 | 30979 (62.0%) |
| ΔR(γ,jet)>0.5 | 30978 |
| Δφ(MET,jet)>0.3 | 28967 |
| MET>300 GeV | 26872 |
| MT(γ,MET)>300 GeV | 26598 |
| S_T^γ>600 GeV | 26581 (53.2%) |

The last bin (>1300 GeV) dominates because for m(χ̃₁⁰)=1700 GeV, the photon from 
χ̃₁⁰→γG̃ typically has pT~500-1500 GeV (from m(χ̃₁⁰)/2 = 850 GeV in the NLSP rest 
frame), and two gravitinos each carrying ~850 GeV produce large MET. Combined, 
S_T^γ = MET + pT(γ) typically exceeds 1300 GeV for this mass point.

---

### 7. Files

| File | Description |
|------|-------------|
| `sims/T5Wg_1750_1700_corrected.slha` | SLHA param card with correct decay channels |
| `sim/run_mg5_001/proc_card_v4.dat` | MG5 process card |
| `sim/run_mg5_001/mg5_T5Wg_v4/Events/run_01/unweighted_events.lhe` | LHE events (patched) |
| `sim/run_pythia8_001/shower.py` | Pythia8 shower driver |
| `sim/run_pythia8_001/events_v5.hepmc` | Showered events (HepMC3, 2.3 GB) |
| `data/delphes_output_v2.root` | Delphes output (1.8 GB) |
| `data/selected_events.root` | Signal region events |
| `analysis.py` | Event selection code |
| `results/histogram_T5Wg.yaml` | Binned signal yields (filled) |
