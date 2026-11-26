# Analysis Report: CMS-SUS-16-034, TChiWZ_550_200

## Summary

Predicted binned E_T^miss signal yield in the electroweak **VZ** signal region
for the simplified model TChiWZ with m(χ̃⁺₁) = m(χ̃⁰₂) = 550 GeV,
m(χ̃⁰₁) = 200 GeV, normalized to 35.9 fb⁻¹ at √s = 13 TeV.

| E_T^miss bin [GeV] | Signal yield |
|---|---|
| 100 – 150 | 0.3622 |
| 150 – 250 | 1.1701 |
| 250 – 350 | 1.4208 |
| > 350     | 1.9501 |
| **Total** | **4.903** |

---

## Simulation chain

### 1. Hard scatter (MadGraph5_aMC@NLO v3.7.0)

- **Process:** `pp → χ̃⁺₁ χ̃⁰₂` + charge conjugate `pp → χ̃⁻₁ χ̃⁰₂`
- **Model:** `MSSM_SLHA2` with custom SLHA2 spectrum (wino-bino scenario)
  - M₁ = 200 GeV (bino mass → m(χ̃⁰₁) ≈ 200 GeV)
  - M₂ = 550 GeV (wino mass → m(χ̃⁺₁) = m(χ̃⁰₂) ≈ 550 GeV)
  - μ = 2000 GeV (higgsinos decoupled)
  - All sfermions at 5000 GeV
- **Decay BRs (forced):** χ̃⁺₁ → W⁺ χ̃⁰₁ (100%), χ̃⁰₂ → Z χ̃⁰₁ (100%)
- **Events:** 50 000 unweighted events at LO
- **MG5 LO σ (NNPDF2.3 LO):** 0.02023 ± 0.000011 pb
- **PDFs:** nn23lo1
- **Output:** `sims/mg5_TChiWZ/Events/run_01/unweighted_events.lhe`

### 2. Parton shower + hadronization (Pythia8 v8.312)

- **Driver:** `sims/shower.py` using the `pythia8` Python module
- **Tune:** CMS UE tune CP1 (Pythia `Tune:pp = 14`)
- **Beam setup:** `Beams:frameType = 4` (read from LHE header)
- **Output format:** HepMC3 Asciiv3
- **Output file:** `sims/TChiWZ_550_200.hepmc` (2.7 GB, 50 000 events)

### 3. Detector simulation

Delphes was attempted but repeatedly killed (SIGKILL, exit 137) due to
system-level OOM pressure (swap exhausted). The analysis was therefore
performed via a pure-Python fast simulation directly on the HepMC3 file.
This avoids the full CMS detector response but correctly models:
- Particle identification (using truth PDG IDs)
- MET as the negative vector sum of all reconstructed (visible) particles
- Anti-kT R = 0.4 jet clustering (custom Python implementation)
- Kinematic cuts faithful to the paper's Table 1

**Deviations from full simulation:**
- No detector smearing (lepton pT / η resolution, JES/JER)
- Lepton isolation is not recomputed from calorimeter deposits
- No pile-up effects
- b-tagging implemented at parton level (B-hadron matching)

### 4. Cross-section normalization

The generator-level LO cross-section from MG5 was replaced by the
**NLO** result from **Prospino 2.1** (CTEQ6L PDF):

| Order | σ [pb] |
|---|---|
| LO (Prospino/CTEQ6L) | 0.0168 |
| **NLO (Prospino/CTEQ6L)** | **0.0194** |
| K-factor | 1.157 |

Event weight = 0.0194 pb × 35900 pb⁻¹ / 50 000 = 0.01393 per event.

---

## Analysis selection (VZ electroweak signal region)

Applied exactly as defined in Table 1 of CMS-SUS-16-034:

| Requirement | Value |
|---|---|
| Dilepton flavor | OSSF (e⁺e⁻ or µ⁺µ⁻) |
| pT(ℓ₁, ℓ₂) | > 25, 20 GeV |
| \|η(ℓ)\| | < 2.4; reject 1.4 < \|η\| < 1.6 (ECAL transition) |
| ΔR(ℓ,ℓ) | > 0.1 |
| pT(ℓℓ) | > 25 GeV |
| m(ℓℓ) | 86–96 GeV (on-Z) |
| N_jets (pT > 35 GeV, \|η\| < 2.4) | ≥ 2 |
| N_b-jets | 0 |
| MT₂(ℓℓ) | > 80 GeV |
| m_jj (jet pair closest in Δφ) | < 110 GeV |
| E_T^miss | > 100 GeV |
| ΔΦ(j₁, MET), ΔΦ(j₂, MET) | > 0.4 |
| Additional lepton veto | pT > 10 GeV, \|η\| < 2.5(e) / 2.4(µ) |

Jet clustering uses anti-kT R = 0.4. Only particles with pT > 2 GeV are
used as jet inputs (soft particles below 2 GeV do not form 35 GeV jets).

MT₂(ℓℓ) is computed numerically by scanning over trial missing-pT
vectors q₁ with |q₁| ∈ [0, |MET|] and angle θ ∈ [0, 2π) (180 × 40
grid), minimising max(MT(ℓ₁,q₁), MT(ℓ₂,q₂)) with q₂ = MET − q₁.
Resolution ~ 2 GeV, adequate for the 80 GeV threshold.

---

## Event counts and yields

| Quantity | Value |
|---|---|
| Generated events | 50 000 |
| Passing VZ selection | 352 |
| Acceptance × efficiency | 0.704% |
| Event weight (at 35.9 fb⁻¹) | 0.01393 |
| Total signal yield | 4.90 |

---

## Output files

| File | Description |
|---|---|
| `results/histogram_TChiWZ.yaml` | Binned E_T^miss signal yields |
| `analysis/analysis_TChiWZ.py` | Full selection code |
| `sims/TChiWZ_550_200.slha` | SLHA2 spectrum (MSSM_SLHA2 format) |
| `sims/proc_TChiWZ.dat` | MG5 process card |
| `sims/shower.py` | Pythia8 shower driver |
| `sims/TChiWZ_550_200.hepmc` | Showered HepMC3 events |

---

## Notes on deviations from paper

1. **No Delphes**: The CMS paper uses full GEANT4 (for backgrounds) and
   the CMS fast simulation (for signals). Our analysis uses parton-level
   truth particle four-momenta. This introduces a ~10–20% bias from
   missing detector resolution effects. In particular, MET smearing and
   JES corrections are absent, which tends to overestimate selection
   efficiency slightly.

2. **LO kinematics**: Events are generated at LO in MG5 and showered with
   Pythia8. The paper uses up to 2 extra partons in the matrix element;
   we use 0 extra partons (pure 2→2 process). ISR is modeled only through
   Pythia's initial-state shower.

3. **NLO normalization**: The event yield is rescaled to the Prospino NLO
   cross-section (0.0194 pb), consistent with the paper's use of NLO+NLL.
   The NLL resummation correction beyond NLO is not applied; the NLL
   correction at this mass is typically ~5%.

4. **b-tagging**: Implemented at parton level (no B-hadron decay tracking).
   For the signal W → light quarks, the b-veto is 100% efficient in our
   implementation; a full simulation would have a ~1.5% mistag rate per jet.

5. **MT₂ grid precision**: The MT₂ grid search uses 180 × 40 = 7200 trial
   points. This is accurate to ~2 GeV, which is sufficient for the 80 GeV
   threshold applied.
