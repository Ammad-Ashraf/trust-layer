# CMS-SUS-16-051 Compressed Signal Region: T2tt_800_400

## Benchmark point

T2tt simplified model: stop pair production, each t̃₁ → t + χ̃⁰₁  
m(stop) = 800 GeV, m(LSP) = 400 GeV, √s = 13 TeV, L = 35.9 fb⁻¹

---

## Generation chain

### 1. Parton-level generation — MadGraph5 v3.7.0

Model: MSSM_SLHA2 (UFO). Process: `p p > t1 t1~`  
Beam energy: 6500 GeV per beam. Events: 50,000.

All SUSY particles except the stop (1000006, 800 GeV) and LSP (1000022, 400 GeV)
were set to 3000 GeV to decouple them. Cross sections:

| Level | σ (pb) |
|-------|--------|
| LO (MadGraph5) | 0.0201 |
| NLO (Prospino) | 0.0272 |
| K-factor | 1.354 |

The MG5-generated `param_card.dat` was used as input to Prospino.

### 2. Parton shower + hadronization — Pythia8 v8.312

CMS UE tune CP1 (`Tune:pp = 14`). Top quarks and stops decay via the SLHA
decay table in `sims/T2tt_800_400.slha` (100% BR: t̃₁ → t + χ̃⁰₁).

**Critical setting**: `SLHA:readFrom = 2` forces Pythia8 to read only the
external SLHA file and skip the MSSM_SLHA2 SLHA block embedded in the LHE
header. The embedded block contains a bino soft mass (MSOFT entry) inconsistent
with the MASS block neutralino mass (400 GeV vs ~101 GeV), causing an infinite
loop in Pythia8's internal SUSY decay width calculator when `readFrom = 1`.

Output: `sims/T2tt_800_400_showered.hepmc` (50,000 events, HepMC3 format).

### 3. Detector simulation — Delphes with delphes_card_CMS.tcl

`DelphesHepMC3` reads the HepMC3 file and applies the CMS detector card.
Output: `data/delphes_T2tt_800_400.root` (50,000 events, Delphes TTree).

---

## Analysis: compressed signal region (CMS-SUS-16-051 Table 3)

### Object definitions

| Object | Selection |
|--------|-----------|
| Electrons | pT > 20 GeV, \|η\| < 2.1 |
| Muons | pT > 20 GeV, \|η\| < 2.4 |
| Jets | pT > 30 GeV, \|η\| < 2.4, ΔR(ℓ,j) > 0.4 |
| b-jets | Delphes BTag bit 0 (CMS medium WP, ~63% eff.) |

### Selection cuts

| Cut | Requirement |
|-----|-------------|
| Presel: MET | > 250 GeV |
| Presel: Lepton | Exactly 1 (e or μ) |
| Presel: Jets | ≥ 2 |
| Presel: b-jets | ≥ 1 |
| Presel: MT | > 150 GeV |
| Presel: min Δφ(MET, J1,2) | > 0.5 (relaxed from 0.8 for compressed) |
| Compressed: N_jets | ≥ 5 |
| Compressed: J1 b-tag | Leading jet NOT b-tagged |
| Compressed: Δφ(MET, ℓ) | < 2 rad |
| Compressed: pT(ℓ) | < 150 GeV |
| Lepton veto | No additional e/μ with pT > 5 GeV |
| Track veto | No isolated track (pT > 10, \|η\| < 2.4, ΔR(trk,ℓ) > 0.3, ΔR(trk,j) > 0.4) |

### Cut-flow table

| Cut | Events passing |
|-----|---------------|
| Total generated | 50,000 |
| MET > 250 GeV | 29,648 |
| Exactly 1 lepton | 5,659 |
| ≥ 2 jets | 5,597 |
| ≥ 1 b-jet | 363 |
| MT > 150 GeV | 257 |
| min Δφ(MET, J1,2) > 0.5 | 246 |
| N_jets ≥ 5 | 119 |
| J1 not b-tagged | 90 |
| Δφ(MET, ℓ) < 2 | 44 |
| pT(ℓ) < 150 GeV | 33 |
| Track veto | 31 |

---

## Results: MET histogram (compressed signal region)

Event weight per generated event:  
`w = σ_NLO × L × 1000 / N_gen = 0.0272 pb × 35.9 fb⁻¹ × 1000 / 50000 = 1.953 × 10⁻² events`

| MET bin (GeV) | Raw events | Expected yield |
|---------------|-----------|----------------|
| [250, 350) | 9 | 0.1758 |
| [350, 450) | 10 | 0.1953 |
| [450, 550) | 4 | 0.0781 |
| ≥ 550 | 8 | 0.1562 |
| **Total** | **31** | **0.6054** |

The last bin is inclusive (all MET ≥ 550 GeV).

---

## Deviations from paper

1. **No ISR reweighting.** CMS applies per-event ISR weights (0.92–0.51 depending on
   N_ISR = 1–6) derived from data/simulation comparisons in Z+jets events. These
   weights would reduce the total signal yield by 15–30%. Not applied here.

2. **Simplified track veto.** The CMS isolated-track veto uses a sum-pT isolation
   variable (pT_sum in a cone) rather than a pure ΔR cone. Here a track is vetoed
   if it has ΔR > 0.3 from the lepton and ΔR > 0.4 from every selected jet. This
   is a reasonable approximation but may differ by O(5–10%) in veto efficiency.

3. **Approximate b-tagging.** Delphes's CMS card uses a parameterized b-tagging
   efficiency (~63% for central b-jets at pT 50–200 GeV). The paper uses the CMS
   DeepCSV medium WP with data/MC scale factors applied. No scale factors here.

4. **LO ISR modeling.** The ISR topology is modeled by Pythia8 internal ISR, not by
   the MLM-matched ME+PS merging that CMS uses for signal. This can affect the
   kinematic distributions, particularly the ISR pT that drives MET in the
   compressed region.

5. **No pileup.** The Delphes CMS card does not simulate pileup. The paper analysis
   uses pileup-reweighted 2016 data conditions (~23 interactions/crossing).

6. **Electron eta cut.** Used \|η\| < 2.1 (central tracker only, excluding gap) rather
   than the CMS 1-lepton selection which sometimes uses \|η\| < 2.5 excluding
   1.444 < \|η\| < 1.566. The difference is small.

---

## Output files

| File | Description |
|------|-------------|
| `sims/proc_card_T2tt.dat` | MadGraph5 process + run card |
| `sims/T2tt_800_400.slha` | SLHA2 file for Pythia8 |
| `sims/shower.py` | Pythia8 shower driver |
| `sims/T2tt_800_400_showered.hepmc` | Showered events (HepMC3) |
| `sims/mg5_T2tt/Events/run_01/unweighted_events.lhe` | LHE events from MG5 |
| `data/delphes_T2tt_800_400.root` | Delphes detector simulation output |
| `analysis/analysis.py` | Analysis script (PyROOT + Delphes library) |
| `results/histogram_T2tt_comp.yaml` | MET histogram yields (this result) |
