# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent demonstrated strong physics understanding and correctly set up a full MadGraph→Pythia8→Delphes→analysis pipeline for TChiWZ(550,200), but spent the majority of the session debugging HepMC3 format incompatibilities with Delphes and never completed the pipeline. The shower was at ~44% when the session ended, so no results were produced.


## Planning

The agent identified the correct analysis strategy early: VZ signal region from CMS-SUS-16-034, on-Z dilepton + dijet + MET bins. It planned the full simulation chain (MadGraph→Pythia8→Delphes→ROOT analysis) and wrote the analysis script proactively while waiting for earlier stages. However, it did not estimate the wall-clock time the pipeline would require or consider reducing N_gen to ensure completion.


## Tool Use

Competent use of Prospino (NLO cross sections for both charge-conjugate channels), MadGraph5, Pythia8, and Delphes. The agent struggled significantly with the HepMC3 output format—Delphes reported 0 events from the initial Pythia8 output because vertex lines were missing or malformed. This required three rewrites of shower.py before the format was correct. The agent also had to fix a Pythia8 xmldoc version mismatch and correct MadGraph5 mass parameters that defaulted instead of reading the SLHA file.


## Scientific Judgment

Good. The agent correctly identified the TChiWZ signal as χ̃±₁χ̃⁰₂ production with W and Z decays, computed both charge-conjugate cross sections (19.8 + 7.75 = 27.55 fb NLO via Prospino), caught the MadGraph mass misconfiguration (904 fb LO vs expected ~18 fb), and verified corrected masses in the LHE output (200/550/550 GeV). The VZ region selection cuts in the analysis script matched the paper description.


## Honesty And Reporting

The agent was honest that results were incomplete—it never claimed to have values it didn't have. However, report.md was left essentially empty (template with no content), and datasets.yaml was an empty array, which provides no useful information for a future agent to continue from.


## Overall Assessment

A technically competent but incomplete run. The agent demonstrated strong physics judgment (correct signal identification, NLO cross sections, mass verification, proper VZ region cuts) and built a correct end-to-end simulation pipeline. However, it spent too much time debugging HepMC3 format issues and chose too large an event sample (50k) without estimating whether the pipeline could complete in the available time. The result is a null submission despite having all the components ready. The critical missing decision was to reduce N_gen when time was running short—even 5k events would have produced usable bin statistics for this signal.


## Strengths

- Correct physics: identified both charge-conjugate production channels and computed NLO cross sections
- Caught and fixed MadGraph5 mass misconfiguration by comparing LO cross section to Prospino NLO
- Persistent debugging of HepMC3 format issues through systematic testing with small event samples
- Wrote a detailed analysis script implementing the full VZ region selection before needing it


## Creative Moves

- Used small event samples (5, 50, 100 events) to debug the HepMC3/Delphes format incompatibility before committing to the full 50k-event run (impact: helpful; evidence: Extracted 50-event test files and ran Delphes on them to verify the format before restarting the full shower. This confirmed the pyhepmc-based writer worked (50/50 events read with realistic MET).)
- Cross-checked MadGraph LO cross section against Prospino NLO to catch mass misconfiguration (impact: helpful; evidence: MG5 reported σ=904.5 fb with default masses vs Prospino NLO σ=19.8 fb. Agent immediately recognized the discrepancy, inspected the param_card, found default masses, and wrote a fix script.)


## Stuck Points

- Three iterations of shower.py to get a HepMC3 format that Delphes could read (missing vertex lines, then wrong vertex format, then missing beam particles for pyhepmc) (impact: major; avoidable: True; evidence: The agent first used pythia8's built-in HepMC3 writer (no vertex lines), then manual ASCII writing (wrong V-line format), then pyhepmc with beam particles. Each iteration required a full re-shower. A quick test with 5 events at the start would have caught this before the first full run.)
- Running 50k events through Pythia8 shower took longer than the remaining session time, and the agent did not reduce N_gen or estimate completion time (impact: major; avoidable: True; evidence: At 22k/50k events with a 1.3 GB HepMC file growing, the shower was still hours from completion. The agent could have used 10k events (sufficient for 4-bin statistics at this cross section) to ensure the pipeline completed within the session.)
- Delphes repeatedly killed by shell timeout on the full event file (impact: moderate; avoidable: True; evidence: Multiple Delphes runs on the full HepMC file were killed. The agent eventually used run_in_background but had already wasted several attempts. This was compounded by the HepMC3 format issue producing 0-event ROOT files.)


## Issues

- The session ended with no results submitted. The agent's pipeline was architecturally correct but never completed because the shower was still running. Reducing N_gen from 50k to 5k–10k would have been sufficient for 4-bin statistics and would have allowed the full pipeline to complete. (severity: critical; evidence: Session ends monitoring Pythia8 at 22k/50k events. The analysis script, Delphes config, and cross sections were all ready. Only wall-clock time prevented completion.)
- Multiple sleep-and-check cycles for Pythia8 and Delphes processes consumed context and time without advancing the work. (severity: moderate; evidence: At least 6 tail/sleep/check cycles for the shower progress between 18k and 22k events, plus earlier cycles for Delphes.)
- Report.md and datasets.yaml were left empty despite the agent having computed cross sections, identified datasets, and written analysis code. A future agent continuing this work would have no structured record of progress. (severity: minor; evidence: report.md contains only the empty template. datasets.yaml is an empty array. The agent recorded some quantities via record-quantity but left the workspace artifacts unfilled.)
