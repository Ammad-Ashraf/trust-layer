# CMS-SUS-16-034 Signal Simulation: TChiWZ_550_200

**Analysis:** CMS EWK VZ signal region  
**Benchmark:** pp → χ̃⁺₁ χ̃⁰₂ → W χ̃⁰₁ Z χ̃⁰₁, m(χ̃⁺₁)=m(χ̃⁰₂)=550 GeV, m(χ̃⁰₁)=200 GeV  
**√s = 13 TeV, L = 35.9 fb⁻¹**

---

## Pipeline

### 1. SLHA Spectrum (`sims/TChiWZ_550_200.slha`)

A pure-wino simplified model spectrum was constructed:
- χ̃⁰₁ (1000022): 200 GeV, bino-like (N₁₁=1), stable LSP
- χ̃⁰₂ (1000023): 550 GeV, wino-like (N₂₂=1)
- χ̃⁺₁ (1000024): 550 GeV, wino-like (U₁₁=V₁₁=1)
- Squarks, gluino, sleptons: 5000 GeV (decoupled)
- DECAY 1000023: χ̃⁰₂ → Z χ̃⁰₁, BR=100%
- DECAY 1000024: χ̃⁺₁ → W⁺ χ̃⁰₁, BR=100%

**Note on mixing:** The χ̃⁰₁–χ̃⁰₂–Z coupling in the MSSM is proportional to N_{i3}N_{j3}* − N_{i4}N_{j4}* (higgsino content). For pure bino/wino eigenstates this coupling is zero at tree level in the matrix-element generator. The Z decay of χ̃⁰₂ is therefore enforced via the SLHA decay table in Pythia8, not via MadGraph explicit decays.

### 2. Hard-Scatter Generation (`sims/proc_TChiWZ_v3.dat`)

- Generator: MadGraph5_aMC@NLO with MSSM_SLHA2 UFO model
- Process: `p p > x1+ n2`, `p p > x1- n2` (Drell-Yan via W*)
- N_gen = 50,000 events, √s = 13 TeV (Ebeam = 6500 GeV)
- PDF: NNPDF2.3 LO (MadGraph default)
- Dynamic renormalization/factorization scales (dynamical_scale_choice=3)
- Output: `sims/events_TChiWZ.lhe` (LHE format, production-only)

### 3. Parton Shower and Hadronization (`sims/shower_TChiWZ.py`)

- Generator: Pythia8 (v8.312), Monash tune (Tune:pp=14)
- Input: LHE with χ̃⁺₁/χ̃⁰₂ as final states (Beams:frameType=4)
- Decays: χ̃⁰₂ → Z χ̃⁰₁ and χ̃⁺₁ → W± χ̃⁰₁ from SLHA tables; Z and W further decayed by Pythia via standard SM branching fractions
- χ̃⁰₁ set as stable LSP (mayDecay=false)
- ISR, FSR, MPI, hadronization all enabled
- Output format: HepMC2 ASCII (`sims/events_TChiWZ_v2.hepmc`, 50,000 events, 3.0 GB)
  - HepMC2 chosen over HepMC3 for compatibility with Delphes `DelphesHepMC2` reader
  - Events include beam protons (PDG 2212, status=4) as required by Delphes

### 4. Detector Simulation (`data/TChiWZ_550_200.root`)

- Simulator: Delphes 3.5 with `delphes_card_CMS.tcl`
- Reader: `DelphesHepMC2`
- Output: 50,000 ROOT events, 1.6 GB
- χ̃⁰₁ particles (neutral, weakly interacting) correctly contribute to MissingET

### 5. Cross-Section Normalization

NLO cross-section from Prospino 2.1:
- Process: pp → χ̃⁺₁ χ̃⁰₂ (Drell-Yan, process code "nn", ipart1=5, ipart2=2)
- m(χ̃⁺₁) = m(χ̃⁰₂) = 550 GeV, √s = 13 TeV
- **σ_NLO = 19.8 fb** (recorded in `ledger.yaml`)

Weight per generated event: σ_NLO × L / N_gen = 19.8 × 35.9 / 50,000 = **0.01422 events/event**

---

## VZ Signal Region Selection (`analysis/analysis_VZ.py`)

Cuts applied following CMS-SUS-16-034 EWK VZ SR definition:

1. **MET > 100 GeV** (preliminary, from paper)
2. **OCSF dilepton pair**: two leptons of same flavor and opposite charge among the two highest-pT leptons
3. **Leading lepton pT > 25 GeV, subleading > 20 GeV**
4. **|η| < 2.4** (muons) or **< 2.5** (electrons, excluding ECAL transition 1.4 < |η| < 1.6)
5. **ΔR(l1, l2) > 0.1** (avoid clone removal artifacts)
6. **On-Z window: 86 < m_ll < 96 GeV**
7. **pT(ll) > 25 GeV** (Z boson system pT)
8. **≥ 2 jets with pT > 35 GeV, |η| < 2.4, not overlapping leptons (ΔR(j,l) > 0.4)**
9. **No b-tagged jets** (b-veto)
10. **Δφ(jet, MET) > 0.4** for all selected jets
11. **m_jj < 110 GeV**: invariant mass of the two jets closest in φ (targeting hadronic W)
12. **MT2(ll) > 80 GeV**: stransverse mass of the dilepton+MET system
13. **Lepton veto**: events with any additional lepton pT > 10 GeV rejected

**MT2(ll) Implementation:** 1D scan over trial invisible-system azimuthal angle θ (200 steps). For each θ, analytically solve the balanced-point condition MT1(r,θ) = MT2(r,θ) via quadratic root-finding. MT2 is the minimum of MT_max(θ) over all θ, also checking boundary conditions r=0 and r=|p_MET|.

---

## Results

| MET bin [GeV] | Expected signal events |
|:---:|:---:|
| 100–150 | 0.199 |
| 150–250 | 0.810 |
| 250–350 | 1.279 |
| > 350 | 1.166 |
| **Total** | **3.455** |

- Events passing VZ SR cuts: **243 / 50,000**
- Selection efficiency: **0.486%** (includes Z→ℓℓ and W→qq' branching fractions)
- Normalization cross-check: σ_NLO × L × ε = 19.8 × 35.9 × 0.00486 = 3.455 ✓

---

## Deviations from Paper

1. **LO PDF vs NLO:** MadGraph uses NNPDF2.3 LO PDF; CMS uses NLO PDFs with matching. The NLO/LO K-factor is absorbed into the Prospino NLO cross-section.

2. **Detector model:** Delphes parameterized detector vs. full GEANT4+CMS reconstruction. Lepton efficiencies, isolation, and b-tagging performance are approximate.

3. **MET resolution:** Delphes uses parametric calorimeter smearing; real CMS MET includes pileup mitigation (Type-1 corrections, PUPPI). With zero pileup in Delphes, MET resolution is better than in data.

4. **Jet energy corrections:** Delphes applies simple smearing; CMS uses full JEC/JER. This affects m_jj distribution near the 110 GeV threshold.

5. **Trigger efficiency:** Paper applies per-event trigger weights; this simulation applies no trigger weight (implicit 100% efficiency after offline cuts).

6. **N_gen = 50,000 vs CMS:** Statistical uncertainty on signal yield is √(243)/243 ≈ 6.4% (Poisson). CMS typically uses O(100k) events for precision.
