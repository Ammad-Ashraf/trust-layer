Status: `DONE`

## What Was Done

Generated T2tt_800_400 signal events (m(stop)=800 GeV, m(neutralino)=400 GeV) through a full LO+PS+detector simulation chain, applied the CMS-SUS-16-051 compressed signal-region selection, and filled the MET histogram normalized to 35.9 fb⁻¹.

### Simulation Chain

**1. Matrix-element generation (MadGraph5_aMC@NLO v3.5.4)**
- Model: `MSSM_SLHA2`
- Process: `p p > t1 t1~` (stop-pair production)
- 50,000 LO events at √s = 13 TeV, `ebeam = 6500 GeV`
- Masses set via `param_card.dat`: stop1 = 800 GeV (PDG 1000006), neutralino1 = 400 GeV (PDG 1000022)
- All other sparticles set to 5000 GeV (effectively decoupled)
- LO generator cross section: 0.02013 pb (consistent with expected stop production at 800 GeV)
- 100% BR: stop1 → t + neutralino1 (set in DECAY block)
- Output: `sim/run_mg5_001/mg5_T2tt/Events/run_01/unweighted_events.lhe`

**2. Parton shower + hadronization (Pythia8.312)**
- LHE events read with `Beams:frameType = 4`
- CMS UE tune CP1 (`Tune:pp = 14`)
- Full top quark decays (top → W b, W → lν or qq') enabled
- Stop and neutralino decays handled by Pythia via SLHA decay table
- HepMC3 Asciiv3 output via `pyhepmc` 3.02.05
- **Key fix**: Each event vertex includes both final-state particles (status=1) and hard-process b/c/t quarks (status=3, Pythia internal status -22/-23) to enable Delphes jet flavor association. Without these parton-history entries, Delphes cannot identify b-jets and applies only the ~1% light-jet mistag rate.
- 50,000 events → `sim/run_pythia8_001/events.hepmc` (3.4 GB)
- Driver script: `sim/run_pythia8_001/shower.py`

**3. Detector simulation (Delphes 3, CMS card)**
- Card: `$DELPHES_DIR/cards/delphes_card_CMS.tcl`
- HepMC3 file split into 5 chunks of 10,000 events to avoid memory kill
- Each chunk processed: `DelphesHepMC3 delphes_card_CMS.tcl chunk_N.root chunk_N.hepmc`
- Merged with `hadd` → `sim/run_delphes_001/v3_delphes_output.root` (50,000 entries)
- Copied to `data/T2tt_800_400_delphes.root`
- **B-tagging convention**: Delphes CMS card uses a single `BTagging` module with `BitNumber 0`, so `BTag & 1 = 1` means b-tagged (not `BTag & 2`). The parametrized efficiency matches CMS medium WP CSVv2 (~60-70% for pT 30-400 GeV).

**4. NLO cross section (Prospino 2.1)**
- Process: `tb` (stop-pair), m(stop) = 800 GeV
- PDFs: CTEQ6L1
- σ_NLO = 0.0272 pb (= 27.2 fb)
- Recorded in `ledger.yaml` via `bin/record-quantity`

### Event Selection

Applied CMS-SUS-16-051 compressed selection (Table 3) using `analysis.py`:

**Preselection:**
- Exactly 1 lepton: electron (pT > 20 GeV, |η| < 1.442) or muon (pT > 20 GeV, |η| < 2.4)
- MET > 250 GeV
- MT > 150 GeV (MT = √(2 pT_lep MET (1 − cos Δφ(lep, MET))))
- min Δφ(J1, J2, MET) > 0.5 (compressed relaxes the standard 0.8 requirement)
- ≥ 2 jets (pT > 30 GeV, |η| < 2.4)
- ≥ 1 b-tagged jet (medium WP)

**Compressed selection (additional cuts):**
- NJ ≥ 5 (ISR-topology requirement)
- Leading jet J1 NOT b-tagged (ISR jet, not b-jet)
- Δφ(MET, lepton) < 2
- Lepton pT < 150 GeV

### Results

| MET bin [GeV] | Raw counts | Expected yield (σ·L/N×count) |
|---|---|---|
| [250, 350) | 89 | 1.7381 |
| [350, 450) | 79 | 1.5428 |
| [450, 550) | 46 | 0.8984 |
| [550, ∞)   | 75 | 1.4647 |
| **Total**  | **289** | **5.6441** |

**Normalization:** EVENT_WEIGHT = σ_NLO [fb] × L [fb⁻¹] / N_gen = 27.2 × 35.9 / 50000 = 0.019530 per event

**Selection efficiency:** ε = 289/50000 = 0.00578 (preselection: 3288/50000 = 0.0658)

Ledger check: σ·L·BR·ε = 0.0272 pb × 35.9 fb⁻¹ × 1 × 0.00578 = 5.64 expected events ✓

## Status

| Artifact | Status |
|---|---|
| `papers/CMS-SUS-16-051.pdf` | read via `bin/read-paper` |
| `datasets.yaml` | complete — T2tt_800_400, 50k events, σ=0.0272 pb |
| `analysis/analysis.py` | complete — CMS-SUS-16-051 compressed selection |
| `analysis.py` (workspace root) | complete — called by `bin/run-analysis` |
| `bin/run-analysis` | passes — all required artifacts present |
| `results/histogram_T2tt_comp.yaml` | filled — 4 MET bins |
| `data/T2tt_800_400_delphes.root` | 50,000 Delphes events |
| `sims/T2tt_800_400.slha` | SLHA2 spectrum for Prospino |
| `ledger.yaml` | complete — σ, L, BR, ε recorded |

## Deviations from Paper

1. **LO instead of NLO generation**: MG5 generates LO hard-scatter events; NLO K-factor is applied via Prospino σ_NLO for normalization. The paper uses NLO+NLL cross sections from the LHC SUSY Cross Section Working Group.

2. **Fast detector simulation (Delphes) instead of full GEANT4**: Delphes with the CMS card parametrizes detector response using efficiency functions. It does not reproduce the full CMS PF-based reconstruction, pileup effects, trigger emulation, or data-driven corrections.

3. **min Δφ threshold**: The paper's preselection uses min Δφ(J1,J2,MET) > 0.8 for the standard selection, but > 0.5 for the compressed selection. We apply 0.5 at preselection level to match the compressed-region definition consistently.

4. **B-tagging**: The Delphes CMS card parametrizes CSVv2 medium WP efficiency as a pT-dependent function (~55–71%), not the full multivariate discriminant. No data-driven b-tag scale factors are applied.

5. **Trigger emulation**: No explicit trigger selection is applied. At Delphes level, MET > 250 GeV implicitly corresponds to the signal-region acceptance; the paper uses online MET triggers with ~100% efficiency at this threshold.
