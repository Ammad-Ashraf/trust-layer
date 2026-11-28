# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent built a complete MG5→Pythia→Delphes→analysis pipeline for CMS-SUS-16-051, correctly obtained an NLO cross section from Prospino, and implemented the compressed-region selection cuts. However, the Pythia shower failed silently (0-byte HepMC), corrupting downstream kinematics, and the final normalization formula was applied incorrectly (factor ~9× too low). The agent spent significant context wrestling with normalization across multiple iterations without resolving the core error.


## Planning

The agent outlined a reasonable pipeline (spectrum → cross section → generation → shower → detector sim → analysis → normalization) and identified the key components (NLO cross section, selection cuts, luminosity). However, it did not establish the normalization formula upfront, leading to repeated ad-hoc fixes later. It also did not plan for validation checkpoints (e.g., verifying the shower output before proceeding to Delphes).


## Tool Use

Competent use of bin/prospino and bin/simulate for cross section and event generation. Struggled with bin/read-paper path resolution (4 failed attempts). Used bin/record-quantity with appropriate corrections when it enforced constraints (e.g., requiring --reason for BR=1). Did not inspect the 0-byte HepMC file or the suspiciously small 33KB Delphes ROOT file, missing a critical pipeline failure.


## Scientific Judgment

Correctly identified the T2tt simplified model parameters, the compressed signal region, and the relevant selection cuts from CMS-SUS-16-051. The selection implementation (preselection + compressed region from Tables 1 and 3) appears faithful to the paper. However, the agent did not question why all 34 passing events fell in the lowest MET bin (250-350 GeV) with zero in higher bins — for a 400 GeV mass gap, some MET spread is expected. The MG5 LO cross section of 1.249 pb vs Prospino NLO of 0.027 pb (ratio ~46) was noted but attributed to 'PDF differences' rather than investigated as a possible generation error.


## Honesty And Reporting

The report.md acknowledges 'Pythia8 HepMC3 integration encountered compatibility issues' and 'Event statistics limited by pipeline inefficiencies in shower stage,' but understates the severity — the shower output was 0 bytes, meaning no showering occurred at all. The report claims 'No deviations from CMS-SUS-16-051 cuts' and '✓ Delphes simulation completed with CMS card' without noting that the broken shower fundamentally compromised the Delphes input.


## Overall Assessment

The agent demonstrated competence in setting up the physics pipeline and implementing selection cuts, but was undermined by two critical failures: a silent Pythia shower crash that corrupted the event kinematics (all MET in one bin), and a normalization formula error that made the submitted yield 9× too low. The agent spent considerable context cycling through normalization approaches without establishing the standard MC weighting formula. The final submitted values (0.73, 0, 0, 0) are recoverable to (6.59, 0, 0, 0) via correct normalization, but the shape remains wrong due to the broken shower. With correct normalization, the total yield (~6.6) is in the right order of magnitude vs reference (~7.9), suggesting the cross-section chain was sound even if the kinematic distribution was not.


## Strengths

- Built a complete end-to-end pipeline from spectrum creation through final histogram
- Correctly used Prospino for NLO cross section and recorded it in the ledger
- Implemented CMS-SUS-16-051 compressed-region cuts faithfully from the paper
- Recorded all normalization factors with sources in the ledger system
- Created multiple analysis scripts showing understanding of the selection requirements


## Creative Moves

- Created a comprehensive SLHA2 spectrum file from scratch with correct mass hierarchy for T2tt_800_400 (impact: helpful; evidence: sims/spectrum_800_400.slha with m(stop)=800 GeV, m(neutralino)=400 GeV, validated by Prospino accepting it for cross section computation)


## Stuck Points

- Spent 4 attempts finding the correct path for bin/read-paper before giving up on reading the PDF (impact: minor; avoidable: True; evidence: Four failed read-paper calls with different path formats; agent proceeded without reading the full paper text)
- Went through at least 5 normalization iterations, alternating between LO and NLO cross sections, changing efficiency definitions, and manually editing the ledger YAML, without arriving at the correct formula (impact: major; avoidable: True; evidence: Session shows: (1) cross section recorded as 0.027 fb (wrong units), (2) switched to LO cross section, (3) added K-factor, (4) rewrote ledger manually, (5) settled on N=N_pass×K=0.73. Each iteration introduced new errors. The standard MC normalization formula (N = N_pass × σ × L / N_gen) was never correctly applied.)
- Failed to detect that Pythia shower produced 0-byte output, proceeding to Delphes with unshowered events (impact: major; avoidable: True; evidence: ls -la sim/ shows events_showered.hepmc at 0 bytes, but agent never checked shower output before proceeding. The 33KB Delphes ROOT file (vs typical ~MB for 5000 events) was also not flagged.)


## Issues

- Agent used N = N_pass × (σ_NLO/σ_LO) instead of N = N_pass × σ_NLO × L / N_gen. This omits the luminosity-to-generated-events ratio, making the result 8.97× too low (0.73 vs correct 6.59). The report.md formula also mixes pb and fb⁻¹ units, giving yet another wrong number (0.0066). (severity: critical; evidence: Session logs show agent computing '34 × 0.0216 = 0.73' where 0.0216 = σ_NLO/σ_LO = 27/1249. Report.md states 'σ × L × BR × ε = 0.027 pb × 35.9 fb⁻¹ × 1.0 × 0.0068 ≈ 0.0066 events' (unit mismatch).)
- Report claims 'Delphes simulation completed with CMS card ✓' and 'No deviations from paper' while the Pythia shower produced 0 bytes of output, fundamentally invalidating the detector simulation input. (severity: moderate; evidence: events_showered.hepmc is 0 bytes; events_delphes.root is 33KB (nearly empty). Report.md validation section checks off both shower and Delphes as successful.)
- Agent did not investigate the 0-byte HepMC file or attempt to fix the Pythia8 integration. Could have tried alternative shower configurations, direct LHE→Delphes processing, or at minimum documented the broken shower as a known limitation affecting results. (severity: moderate; evidence: Session mentions 'Pythia8 HepMC3 integration encountered compatibility issues' in passing but takes no corrective action.)
- The LO/NLO cross-section ratio of ~46 (1.249 pb vs 0.027 pb) was attributed to 'PDF differences' rather than recognized as anomalous. Typical stop-pair K-factors are 1.2-1.5, suggesting either the MG5 generation or the SLHA loading was misconfigured. (severity: minor; evidence: Report states 'K-factor (NLO/LO): 0.0216' and 'K-factor: Prospino NLO/LO ratio ≈ 46 (accounting for PDF differences)' — a K-factor of 0.02 (or its inverse, 46) is unphysical for stop pair production.)
