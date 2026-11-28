# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent executed a complete MadGraph5→Pythia8→Delphes→analysis pipeline for T5Wg gluino pair production. It overcame multiple technical obstacles (SLHA2 format, Pythia8 version mismatch, MODSEL block in LHE, charge conservation in decay tables, HepMC file size) and produced internally consistent results with a fully documented normalization chain. The final yield (3.6 events) is ~15× below the reference, primarily due to a low NLO cross section (2.68 fb vs ~10 fb expected at NLO+NLL) and Delphes efficiency losses.


## Planning

Clear and appropriate pipeline: generate LHE events (MadGraph5), shower with SUSY decays (Pythia8), detector simulation (Delphes CMS card), apply analysis cuts, normalize with Prospino NLO cross section. The agent prepared components in parallel where possible (e.g., writing analysis script while Pythia8 ran). The simulation chain covers all required steps for a recast.


## Tool Use

Strong adaptation to tool failures. The agent navigated MadGraph5's MSSM_SLHA2 model requirements, debugged Pythia8 XML version mismatches (8.312 vs 8.313), fixed MODSEL block propagation through LHE files, and correctly used bin/prospino, bin/record-quantity, and bin/run-analysis. The HepMC file size issue (60KB/event → 3GB total, initially 200KB/event) was caught and fixed by killing the process and rewriting a minimal writer. Photon efficiency ROOT file reading was attempted multiple times with uproot before the agent manually extracted the needed values.


## Scientific Judgment

Mostly sound. The agent correctly identified: (1) need for NLO cross section from Prospino rather than LO MadGraph value; (2) photon ID scale factors to correct Delphes-vs-data efficiency differences; (3) trigger efficiency from the paper; (4) proper SUSY decay chain setup (χ̃⁰₁→γG̃, χ̃±₁→W±G̃ with BR=1). The gluino 3-body decay structure (50/50 to neutralino/chargino + quarks) is physically reasonable for the T5Wg topology. One weakness: the agent did not question whether Prospino's NLO-only cross section with CTEQ6 PDF might be systematically low compared to NLO+NLL values used by CMS, nor attempt to validate against published cross section tables.


## Honesty And Reporting

Excellent. The report explicitly lists five deviations from the paper (Delphes vs FullSim, photon isolation approximation, no pile-up, LO matrix element, fixed BRs). The agent did not overclaim accuracy. The cutflow, normalization accounting, and artifact table are clear and reproducible. The ledger product exactly matches the histogram total (3.595), demonstrating careful internal consistency checks.


## Overall Assessment

A technically competent run that executed the full simulation chain correctly and produced traceable, internally consistent results. The agent demonstrated strong debugging skills in resolving multiple SLHA/Pythia8 issues and produced a well-documented report with honest limitations. The main shortcoming is a ~15× yield deficit driven primarily by using Prospino NLO-only with CTEQ6 (yielding 2.68 fb vs ~10 fb at NLO+NLL), compounded by Delphes parametrization effects. The agent did not cross-check its cross section against published values, which would have flagged the discrepancy. Despite the numerical inaccuracy, the methodology is sound and the artifacts are clear enough for another agent to continue.


## Strengths

- Complete simulation chain with no shortcuts — full MadGraph5+Pythia8+Delphes pipeline rather than estimating from simplified models
- Strong technical debugging: resolved Pythia8 version/XML mismatch, SLHA2 format issues, MODSEL propagation through LHE, charge conservation in decay tables
- Careful normalization accounting with cross-verified ledger product matching histogram total
- Applied data-driven photon ID scale factors from the provided efficiency ROOT file rather than ignoring detector-level corrections
- Transparent and well-structured report with explicit deviation listing


## Creative Moves

- Patched the LHE file's embedded SLHA block to include MODSEL and correct decay tables, since Pythia8 reads the LHE SLHA before the external file (impact: helpful; evidence: Session shows the agent discovered Pythia8 wasn't enabling SUSY mode because the LHE-embedded SLHA lacked MODSEL. Patched both the full and test LHE files in-place.)
- Killed the runaway HepMC writer (200KB/event × 50k = 10GB) and rewrote a minimal final-state-only HepMC3 writer (60KB/event) (impact: helpful; evidence: Agent detected the file growing too large at ~16k events, killed the process, and wrote a stripped-down version keeping only final-state particles needed by Delphes.)
- Computed average photon ID scale factor from the provided ROOT efficiency file by extracting bin values and dividing by Delphes barrel efficiency (impact: helpful; evidence: After struggling with uproot TH2F reading, the agent extracted efficiency values (0.848, 0.809 for inner/outer barrel) from the highest ET bin and computed SF = data_eff/0.95.)


## Stuck Points

- Multiple SLHA format iterations before Pythia8 accepted the file — SLHA2 blocks, MODSEL placement, charge conservation in gluino decays, and LHE-embedded SLHA all needed separate debugging passes (impact: moderate; avoidable: True; evidence: At least 6 SLHA rewrites and test runs before the shower succeeded on the 100-event test. Much of this could have been avoided by examining the default SLHA card more carefully upfront and understanding that Pythia8 reads the LHE-embedded SLHA first.)
- Uproot TH2F reading for photon efficiency — multiple failed attempts with different APIs before giving up and extracting values manually (impact: minor; avoidable: True; evidence: Five attempts using member(), extent(), values() etc. failed due to uproot version/API differences. The agent eventually used to_numpy() correctly but spent ~10 minutes on this.)


## Issues

- Prospino NLO cross section with CTEQ6 PDF (2.68 fb) is approximately 3-5× lower than the NLO+NLL values with modern PDFs (~8-12 fb) used by CMS for SMS interpretations at m(g̃)=1750 GeV. The agent did not attempt to validate against published cross section tables or use NLO+NLL order. (severity: major; evidence: Prospino was called with '--order NLO' and CTEQ6 (default). The resulting 2.68 fb is the dominant source of the yield deficit. The agent ran 'bin/prospino help-process gg' but did not explore NLO+NLL options or cross-check against literature values.)
- No validation of the cross section against published SMS cross section tables or the CMS-SUS-16-046 paper's own values. CMS typically cites the LHC SUSY Cross Section Working Group reference values. (severity: moderate; evidence: The agent accepted the Prospino output at face value without sanity-checking against known reference cross sections for gluino pair production, which are widely published.)
- Several sleep-and-check cycles while monitoring Pythia8 and MadGraph5 runs, plus confusion about whether the background Pythia8 process had finished when the shell notification fired. (severity: minor; evidence: The agent ran 'sleep 5', 'sleep 10' to check Pythia8 output, and was confused when the shell returned but the Python process (PID 2684) was still running.)
