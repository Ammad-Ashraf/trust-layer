# CMS-SUS-16-046 T5Wg Signal Simulation Report

## Benchmark Point

T5Wg simplified model: m(g̃) = 1750 GeV, m(NLSP) = 1700 GeV, m(G̃) ≈ 0 GeV  
√s = 13 TeV, L = 35.9 fb⁻¹

## What Was Produced

Binned signal yields in S_T^γ = p_T^miss + Σ p_T(γ_i):

| S_T^γ bin [GeV] | Raw MC events | Expected yield |
|----------------|---------------|----------------|
| [600, 800)     | 30            | 0.3524         |
| [800, 1000)    | 23            | 0.2736         |
| [1000, 1300)   | 24            | 0.2850         |
| [1300, ∞)      | 16            | 0.1909         |
| **Total**      | **93**        | **1.1019**     |

## Simulation Chain

### 1. Hard-process generation (MadGraph5_aMC@NLO v3.7.0)

Process: `pp → g̃ g̃` at LO using the `MSSM_SLHA2` UFO model.  
10,000 events generated at √s = 13 TeV (Ebeam = 6500 GeV each).  
LO cross section from MadGraph: σ_LO = 1.453 fb.

The SLHA2 spectrum (`sims/T5Wg_1750_1700.slha`) defines:
- m(g̃) = 1750 GeV, m(χ̃₁⁰) = m(χ̃₁±) = 1700 GeV, all squarks/sleptons at 5000 GeV
- χ̃₁⁰ is wino-like (NMIX N₁₂ = 1), so χ̃₁⁰ → γ G̃ with 100% BR
- Gluino BRs: g̃ → q q̄ χ̃₁⁰ (5×10%, u/d/s/c/b quarks); g̃ → q q̄' χ̃₁± (4×12.5%)
- χ̃₁± → W± G̃ (100%), gravitino is stable

The param card for MadGraph was derived from the model's default (`param_card_default.dat`) with masses patched to the benchmark values, ensuring all SLHA2-required mixing matrices (DSQMIX, USQMIX, SELMIX, etc.) were present.

### 2. Parton shower and SUSY decays (Pythia8.313)

LHE events showered with Pythia8 (`sims/shower_T5Wg.py`):
- `Beams:frameType = 4` (LHE input)
- `SLHA:readFrom = 2`, `SLHA:file = …`, `SLHA:useDecayTable = on`
- CMS CP1 underlying-event tune (`Tune:pp = 14`)
- ISR/FSR/MPI and hadronisation all enabled

HepMC3 output was written using a manual `GenEvent`/`GenVertex`/`GenParticle` construction because this Pythia8 build does not expose `Event::to_hepmc3()`.

### 3. Detector simulation (Delphes 3.5.0)

`DelphesHepMC3` with `delphes_card_CMS.tcl`. Output: `data/T5Wg_1750_1700.root`, 10,000 events.

### 4. Event selection (`analysis/analysis.py`)

Following Table 1 of CMS-SUS-16-046:

**Preselection**
- ≥1 photon with p_T > 180 GeV, |η| < 1.44 (barrel ECAL)
- ΔR(leading γ, jet) > 0.5 for all Delphes jets
- Δφ(p_T^miss, jet) > 0.3 for all jets with p_T > 100 GeV

**Signal region**
- p_T^miss > 300 GeV
- M_T(γ, p_T^miss) > 300 GeV, where M_T = √(2 p_T^γ p_T^miss (1 − cos Δφ))
- S_T^γ = p_T^miss + Σ p_T(γ_i) > 600 GeV

Pass rates: 1997/10000 at preselection, 93/10000 in the signal region.

### 5. Normalisation and corrections

Event weight = σ_NLO × L / N_gen = 3.96 fb × 35.9 fb⁻¹ / 10,000 = 0.014216 per event  
NLO cross section σ_NLO = 3.96 fb from Prospino (m(g̃) = 1750 GeV, 13 TeV). K-factor ≈ 2.72.

**Photon efficiency scale factor** (applied per event):  
The Delphes CMS card applies a flat 95% barrel efficiency. CMS measured efficiencies from `object_efficiencies/photon_eff_LoosePixelVeto.root`:  
- |η| < 0.8: 0.8481; 0.8 < |η| < 1.44: 0.8087  
Scale factor = CMS_eff / Delphes_eff (0.892 or 0.851 depending on photon η).

**Trigger efficiency**: 0.943 (flat, from paper Section 5).

## Deviations from the Paper

1. **Lepton veto not applied.** The analysis vetoes events with electrons or muons with p_T > 25 GeV. With ~50% of gluino decays proceeding through χ̃₁± → W± G̃ and BR(W → lν) ≈ 33%, roughly 25–30% of signal events contain a reconstructed lepton. Omitting this veto inflates the signal yield by a comparable fraction. This is the dominant systematic deviation.

2. **LO generation with NLO rescaling.** Events were generated at LO; the NLO cross section is applied as a flat K-factor (≈ 2.72). NLO generation with matched parton shower would redistribute kinematic distributions slightly (harder ISR radiation) but is unavailable in this setup.

3. **Photon efficiency uses η-averaged values.** The CMS efficiency is taken as a constant in two η bins rather than a full 2D (p_T, η) look-up table from the ROOT file. At the high photon p_T relevant here (> 400 GeV) the efficiency is relatively flat, so the error is small.

4. **Limited MC statistics.** 93 signal-region events give a ~10% statistical uncertainty on the total yield and ~20–25% per bin. A production sample of ~100k events would reduce this.

5. **Jet pT threshold for ΔR isolation.** The paper specifies the ΔR(γ, jet) > 0.5 requirement for jets with p_T > 30 GeV, |η| < 3. The implementation applies it to all jets in the Delphes collection (no explicit pT floor), which may reject a small number of additional events due to soft jets near the photon.
