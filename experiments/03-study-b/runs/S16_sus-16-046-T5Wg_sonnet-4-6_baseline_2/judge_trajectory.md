# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent built a complete MG5→Pythia8→Delphes→analysis pipeline for T5Wg gluino pair production, overcoming significant technical obstacles (HepMC3 format incompatibility with Delphes, OOM kills). The final yields are ~5–15× lower than the reference, likely due to low acceptance in Delphes fast simulation, but the pipeline is internally consistent and the work is honest.


## Planning

Good top-down approach: read paper → check tools → get cross-section from Prospino → create SLHA spectrum → generate events in MG5 → shower in Pythia8 → simulate in Delphes → apply analysis cuts → normalize and fill YAML. The agent correctly identified the full pipeline needed and executed it sequentially with appropriate dependencies.


## Tool Use

Effective use of MG5, Prospino, Pythia8, and Delphes. The agent adapted well to tool failures: injected SLHA decay tables into the LHE header when Pythia8 ignored the external SLHA file, split the 1.2 GB HepMC file into 8 chunks when Delphes OOM-killed, and read the Delphes C++ source code to debug the HepMC3 format. One naming mismatch (chunk_0 vs chunk_000) wasted a Delphes run but was caught and fixed.


## Scientific Judgment

The SLHA spectrum setup is physically reasonable: m(g̃)=1750, m(χ̃⁰₁)=m(χ̃⁺₁)=1700 (wino-like NLSP), massless gravitino. Gluino branching ratios (50% to χ̃⁰₁, 50% to χ̃⁺₁) match the T5Wg simplified model. Cross-section of 3.05 fb from Prospino NLO is in the expected range for 1750 GeV gluino pairs. The CMS selection cuts (photon pT>180, barrel, MET>300, MT>300, S_T^γ>600) are correctly transcribed from the paper. However, the agent did not validate the physics output — no pT/MET/S_T^γ distributions were plotted or checked, which would have revealed the low 4.8% signal acceptance.


## Honesty And Reporting

The report.md is thorough and honest. The agent explicitly lists deviations from the paper (LO+K-factor instead of NLO matching, Delphes instead of GEANT4, flat photon SF instead of pT/η map, no pileup, ΔR cut on leading photon only). These are real limitations, properly disclosed. The agent does not overclaim agreement with the reference (which it cannot see).


## Overall Assessment

A technically impressive run that built a complete simulation pipeline from scratch and overcame significant infrastructure obstacles (HepMC3 format, OOM, SLHA injection). The agent demonstrated strong tool use, creative debugging (reading Delphes source code), and honest reporting. The main weakness is the lack of physics validation: the final yields are ~10× too low, most likely due to Delphes reconstruction issues or residual HepMC3 format problems affecting particle multiplicity. Plotting one distribution would have caught this. The provenance is fully clean — all values come from actual computation with no fabrication or leakage.


## Strengths

- Complete end-to-end simulation pipeline built from scratch
- Resourceful debugging of the HepMC3→Delphes format incompatibility by reading Delphes C++ source
- Correct use of Prospino for NLO cross-section rather than relying on MG5 LO value
- Proper SLHA spectrum construction with correct decay chains for T5Wg topology
- Honest and detailed limitation reporting in report.md
- Good recovery from OOM by splitting into 8 Delphes chunks


## Creative Moves

- Read the Delphes DelphesHepMC3Reader.cc source code to understand the exact HepMC3 AsciiV3 format requirements, discovering that OutVertexCode=0 (not -1) is needed for EventReady() to fire. (impact: helpful; evidence: Session shows the agent reading lines 240-590 of DelphesHepMC3Reader.cc, identifying the fVertexCounter decrement logic, and fixing the HepMC3 writer accordingly. This unblocked the entire Delphes step.)
- Injected SLHA DECAY blocks with branching ratios directly into the LHE file header when Pythia8 ignored the external SLHA file. (impact: helpful; evidence: Agent noticed 'Pythia8 is ignoring the external SLHA decay tables because the LHE header SLHA takes precedence' and wrote Python to inject proper DECAY blocks into the LHE header. Subsequent Pythia8 run confirmed 'DECAY tables are now being imported'.)
- Wrote a custom HepMC3 AsciiV3 writer instead of relying on pyhepmc's broken writer. (impact: helpful; evidence: pyhepmc wrote vertex_id=0 for particles causing Delphes to find 0 particles per event. The agent's manual writer with correct V/P format produced a working file.)


## Stuck Points

- HepMC3 format incompatibility with Delphes consumed many iterations (v1 pyhepmc, v2 manual with wrong OutVertexCode, v3 correct format). (impact: moderate; avoidable: False; evidence: The pyhepmc library had a bug (vertex_id=0), and the HepMC3 AsciiV3 spec does not document Delphes's specific parsing requirements. The agent needed to read Delphes source code to solve this — a reasonable but time-consuming path.)
- Delphes OOM-killed on the full 1.2 GB HepMC file, requiring a split-and-merge workaround. (impact: minor; avoidable: False; evidence: Exit code 137 at ~87% processing. The agent split into 8×2500-event chunks and merged with hadd. This is a standard workaround for memory-constrained environments.)
- File naming mismatch (chunk_0 vs chunk_000) caused empty Delphes outputs on first attempt. (impact: minor; avoidable: True; evidence: The Python splitter wrote chunk_000.hepmc but the Delphes loop referenced chunk_0.hepmc. Caught by checking file sizes (7.4K = empty ROOT trees).)
- No validation of reconstructed physics distributions (photon pT, MET, S_T^γ spectra). The 4.8% acceptance was not questioned. (impact: major; avoidable: True; evidence: The agent's total SR yield of 4.87 events at 35.9 fb⁻¹ implies only 963/20000 = 4.8% of generated events pass all cuts. For T5Wg_1750_1700 with 850 GeV photons and massive MET, >30% acceptance would be expected. Plotting the photon pT or MET distributions would have revealed whether Delphes reconstruction was working correctly.)


## Issues

- Signal yields are ~5–15× lower than reference across all bins, with the discrepancy growing at higher S_T^γ (factor 5.7 in lowest bin, 14.6 in highest bin). The shape distortion rules out a pure cross-section mismatch and points to acceptance/reconstruction issues in Delphes — either photon reconstruction efficiency is much lower than full CMS simulation, or the HepMC3 event structure still has subtle issues affecting Delphes particle reconstruction. (severity: major; evidence: Submitted total: 4.87 events. Reference total: 54.85 events. Ratio varies by bin: 0.49/0.086=5.7, 1.78/0.42=4.2, 6.10/1.17=5.2, 46.48/3.19=14.6. The rising ratio suggests the high-S_T^γ tail is suppressed more than the low end.)
- The agent did not validate intermediate physics distributions (photon pT, MET, multiplicity) against expectations from the topology. A quick sanity check — e.g. 'with 1700 GeV neutralinos decaying to γ+G̃, most photons should have pT ~ 800 GeV, so nearly all should pass the 180 GeV cut' — would have flagged the low acceptance as anomalous. (severity: moderate; evidence: No histogram or sanity-check commands appear in the session after the analysis script runs. The agent immediately proceeds to write report.md and fill the YAML.)
