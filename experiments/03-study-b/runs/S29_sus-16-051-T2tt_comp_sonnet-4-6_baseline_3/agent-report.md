# Report: CMS-SUS-16-051 Compressed Signal Region — T2tt_800_400

## Summary

This analysis predicts the binned MET signal yield for the T2tt simplified model at m(stop)=800 GeV, m(χ̃₁⁰)=400 GeV in the **compressed signal-region selection** of CMS-SUS-16-051 (arXiv:1706.04402), normalized to 35.9 fb⁻¹ at √s=13 TeV.

---

## Simulation chain

### 1. Matrix-element generation (MadGraph5 v3.7.0)

- **Process**: `p p > t1 t1~, (t1 > t n1), (t1~ > t~ n1)` using the `MSSM_SLHA2` UFO model  
- **Masses**: m(stop₁) = 800 GeV, m(χ̃₁⁰) = 400 GeV; all other SUSY particles decoupled at 5 TeV  
- **Decays**: 100% BR(stop → t + χ̃₁⁰)  
- **Events generated**: 50,000 unweighted events  
- **Centre-of-mass energy**: √s = 13 TeV  
- **LO cross-section from MG5**: 0.04462 pb (NNPDF3.0 LO)  
- Output: `sims/mg5_T2tt_800_400/Events/run_01/unweighted_events.lhe`

### 2. Parton shower + hadronization (Pythia8 v8.312)

- **Settings**: CMS UE tune CP1 (`Tune:pp = 14`), beams from LHE header (`Beams:frameType = 4`)  
- **HepMC2 output**: The HepMC2 file includes  
  - All Pythia8 final-state particles (`isFinal() == True`, HepMC status=1) for detector simulation  
  - Hard-scatter parton-level quarks/gluons (`status == -23`, abs(id) ≤ 5, HepMC status=3) so Delphes JetFlavorAssociation can correctly identify b-jets  
- Output: `sims/T2tt_800_400_v2.hepmc` (3.6 GB, 50,000 events)

### 3. Detector simulation (Delphes v3, CMS card)

- **Card**: `$DELPHES_DIR/cards/delphes_card_CMS.tcl`  
- The file was split into 5 chunks of 10,000 events to avoid OOM; each chunk was processed individually  
- Output: `data/delphes_v2_chunks/chunk_000{0..4}.root`  
- Jet b-tagging: single WP (medium, `BitNumber 0`) with efficiency `0.85 × tanh(0.0025 pT) × (25/(1+0.063 pT))` for b-jets and ∼1% mistag for light jets

### 4. Cross-section normalization (Prospino 2)

- **Process**: stop–antistop pair production (`tb`, ipart1=1 for stop₁)  
- **Result**: σ(NLO) = **0.0272 pb** (K = 1.71 relative to Prospino LO of 0.0159 pb)  
- Note: the official LHC SUSY Cross-Section Working Group value at NLO+NLL for m(stop)=800 GeV is ≈0.0244 pb; Prospino NLO (without NLL resummation) gives 0.0272 pb. The Prospino NLO value is used here.

**Event weight**: σ_NLO × L / N_gen = 0.0272 pb × 1000 fb/pb × 35.9 fb⁻¹ / 50,000 = **0.01953 events/generated_event**

---

## Event selection

The selection follows the preselection and compressed signal-region criteria from Tables 1 and 3 of CMS-SUS-16-051.

### Preselection
| Cut | Requirement |
|-----|-------------|
| Lepton | Exactly 1 electron (pT > 20 GeV, |η| < 1.442) OR 1 muon (pT > 20 GeV, |η| < 2.4); isolation: psum_T/plep_T < 0.1 (Delphes `IsolationVar < 0.1`) |
| Extra leptons | Veto events with additional e/μ (Delphes enforces this by requiring exactly 1 isolated lepton) |
| MET | > 250 GeV |
| MT | > 150 GeV, computed as √(2 pT^lep × MET × (1 − cos Δφ(lep, MET))) |
| Jets | ≥ 2 jets with pT > 30 GeV, |η| < 2.4 |
| b-jets | ≥ 1 b-tagged jet (Delphes medium WP, `BTag > 0`) |

### Compressed selection (Table 3)
| Cut | Requirement |
|-----|-------------|
| NJ | ≥ 5 jets |
| J1 b-tag | Leading jet NOT b-tagged |
| Δφ(MET, lep) | < 2 rad |
| min Δφ(J1,2, MET) | > 0.5 rad (relaxed from 0.8 in preselection) |
| Lepton pT | < 150 GeV |

### Deviations from paper

1. **Isolated track veto**: not implemented. The paper vetoes events with additional isolated charged-PF tracks; this is not directly accessible in Delphes without generator-level track matching.

2. **min Δφ(J1,2, MET) for preselection**: The paper uses 0.8 rad for the standard preselection but relaxes to 0.5 for the compressed selection. I apply 0.5 for the compressed selection (the actual cut applied to these events). The stricter 0.8 rad cut is NOT applied first.

3. **Lepton isolation**: The paper uses a mini-isolation cone DR = min(0.2, max(0.05, 10 GeV/pT^lep)), but Delphes uses a fixed DR = 0.5 cone. This may affect the lepton selection slightly.

4. **b-tagging WP**: The paper uses both medium and tight WPs; the Delphes CMS card provides only one WP (medium). The compressed selection requires ≥1 b-tag (medium WP), which is implemented.

5. **ISR reweighting**: The paper applies ISR jet-multiplicity reweighting to signal events. This reweighting (varying from 0.92 for N_ISR=1 to 0.51 for N_ISR=6) is not applied here. This would reduce the yields by ~10-20%.

6. **Fast simulation vs GEANT4**: CMS used their fast simulation for signal samples; Delphes provides a comparable parameterized simulation.

---

## Cutflow (per 10,000 events, chunk 0)

| Cut | Events passing |
|-----|---------------|
| Generated | 10,000 |
| Exactly 1 lepton | 1,888 |
| + MET > 250 GeV | 335 |
| + MT > 150 GeV | 186 |
| + ≥2 jets, ≥1 b-tag | 159 |
| + NJ ≥ 5 | 68 |
| + J1 not b-tagged | 55 |
| + Δφ(MET, lep) < 2 | 26 |
| + min Δφ(J1,2, MET) > 0.5 | 26 |
| + lep pT < 150 GeV | 22 |

---

## Results

Expected signal yields in the compressed MET bins at 35.9 fb⁻¹:

| MET bin [GeV] | Events (this analysis) |
|---------------|------------------------|
| 250–350       | 0.879                  |
| 350–450       | 0.430                  |
| 450–550       | 0.078                  |
| >550          | 0.059                  |
| **Total**     | **1.45**               |

The total expected signal (1.45 events) corresponds to a selection efficiency of ~0.15% (74/50,000 events pass). This is physically reasonable because:
- The compressed selection targets the mass corridor region (Δm ≈ m_top), but T2tt_800_400 has Δm = 400 GeV which is >> m_top = 173 GeV
- The lep pT < 150 GeV cut is quite restrictive for the high-Δm scenario
- NJ ≥ 5 combined with J1 not b-tagged requires a hard ISR jet as the leading jet

---

## Artifacts

| File | Contents |
|------|----------|
| `sims/T2tt_800_400.slha` | SLHA param card (stop=800, chi=400 GeV) |
| `sims/proc_T2tt.dat` | MadGraph5 process card |
| `sims/shower.py` | Pythia8 shower driver (HepMC2 output with status=3 partons) |
| `sims/mg5_T2tt_800_400/Events/run_01/unweighted_events.lhe.gz` | MG5 LHE events |
| `sims/T2tt_800_400_v2.hepmc` | Pythia8-showered HepMC2 events |
| `data/delphes_v2_chunks/chunk_000*.root` | Delphes-simulated events (5 × 10k) |
| `analysis/analysis.py` | Selection code |
| `results/histogram_T2tt_comp.yaml` | Final MET histogram |
