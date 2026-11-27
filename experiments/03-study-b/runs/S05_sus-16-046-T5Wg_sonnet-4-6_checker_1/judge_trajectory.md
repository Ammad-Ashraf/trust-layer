# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent successfully executed a full MG5+Pythia8+Delphes simulation chain for a compressed T5Wg SUSY spectrum, diagnosing and fixing three non-trivial technical blockers (HepMC3 vertex structure, gravitino Delphes invisibility, Prospino SLHA parsing). The final yields are internally consistent but ~3× too low due to a 59% Pythia8 shower failure rate that the agent documented but did not attempt to fix.


## Planning

The agent followed a sensible linear plan: read paper → generate events (MG5) → get NLO cross section (Prospino) → shower (Pythia8) → detector sim (Delphes) → analysis → results. It parallelized Prospino and shower preparation while MG5 ran. It drafted report.md and analysis.py while waiting for the shower. Task decomposition was reasonable, though the agent did not create an explicit plan document.


## Tool Use

Generally competent. The agent correctly used bin/read-paper, bin/simulate, bin/prospino, bin/record-quantity, and bin/run-analysis. It adapted well when tools failed — creating stripped SLHA files for Prospino, reformatting HepMC3 for Delphes, modifying the Delphes card. The main tool-use failure was accidentally launching two concurrent shower processes writing to the same file, requiring a restart. The agent also spent significant context on initial paper-reading failures before finding the correct invocation path.


## Scientific Judgment

Mixed. Strong points: correct NLO normalization with Prospino, proper N_gen=50,000 denominator for event weight, identification that the gravitino must be invisible in Delphes, correct CMS signal region cuts from the paper, appropriate use of the photon efficiency map. Weak point: accepting a 59% shower failure rate without investigation — this is an unusually high failure rate that likely stems from the compressed spectrum (Δm=50 GeV) causing Pythia8 difficulty with the three-body gluino decay kinematics. The agent could have tried MG5-level decays (MadSpin) or adjusted Pythia8's TimeShower/SpaceShower parameters. The K-factor stated in the report (2.59×) is Prospino's internal NLO/LO ratio, not MG5's — this is correct but the phrasing is confusing.


## Honesty And Reporting

Excellent. The report clearly documents the 59% shower failure, the gravitino Delphes fix, the HepMC3 vertex workaround, and the photon efficiency map interpretation uncertainty. The agent does not overclaim — it notes that the shower failures 'reduce statistical power but do not bias the physics prediction,' which is partially correct (the normalization is unbiased but the kinematic shape is biased by differential survival rates). The deviations section is thorough and actionable.


## Overall Assessment

A technically impressive run that demonstrated strong debugging and adaptation skills — the agent solved three non-trivial blockers (HepMC3 vertices, gravitino invisibility, Prospino SLHA parsing) that would have produced zero or meaningless output. The simulation pipeline is correctly architected and the normalization is internally self-consistent. However, the 59% Pythia8 shower failure rate is the dominant systematic error, producing yields ~3× below the reference with distorted bin shapes. The agent correctly documented this limitation but missed an opportunity to diagnose and mitigate it. The final result is an honest, well-documented underprediction rather than a fabrication or lucky match — the kind of outcome where the methodology is sound but a single unresolved technical issue dominates the error budget.


## Strengths

- Identified and fixed the gravitino invisibility bug in Delphes (mean MET 87→925 GeV), which was the single most critical physics issue
- Correctly diagnosed the HepMC3 vertex structure problem and wrote a reformatter rather than re-running the entire 40-minute shower
- Proper NLO normalization: used Prospino for the cross section and N_gen=50,000 as the denominator, not the 20,522 surviving events
- Created a well-structured analysis.py that passed the preflight vectorization check
- Thorough report.md documenting all deviations from the published analysis


## Creative Moves

- Reformatted the HepMC3 file by injecting synthetic beam protons and vertex lines rather than re-running the 40-minute Pythia8 shower (impact: helpful; evidence: reformat_hepmc.py adds status-4 proton beam particles and a production vertex to each event. After reformatting, Delphes processed all 20,522 events successfully.)
- Created a stripped SLHA file (no blank lines, no partial-width rows) to work around Prospino's Fortran parser limitations (impact: helpful; evidence: Three SLHA iterations: T5Wg_1750_1700.slha (full, failed), T5Wg_1750_1700_xs.slha (failed), T5Wg_1750_1700_xs2.slha (succeeded with Prospino). Agent read the Fortran source (Xread_les_houches.f) to diagnose the parsing issue.)
- Modified the Delphes CMS card to add gravitino as invisible in ECAL, HCAL, and NeutrinoFilter (impact: helpful; evidence: Without the fix, mean reco MET was 87 GeV (gravitino depositing energy in HCAL); with it, 925 GeV. Agent diagnosed this by comparing GenMET and reco MET distributions.)


## Stuck Points

- Initial MG5 run used default gluino mass (607 GeV) instead of 1750 GeV because the SLHA file was not properly injected into MG5's Cards directory (impact: moderate; avoidable: True; evidence: First run produced σ=4.77 pb (consistent with ~600 GeV gluinos). Agent had to rewrite the launch card and rerun MG5. Lost ~15 minutes of generation time.)
- Accidentally ran two Pythia8 shower processes simultaneously, corrupting the output HepMC file (impact: moderate; avoidable: True; evidence: Session shows two PIDs (3589, 3667) both writing to events.hepmc. Agent killed both, cleaned up, and restarted — losing ~10 minutes of shower progress.)
- Multiple rounds of paper-reading failures due to incorrect bin/read-paper invocation path (impact: minor; avoidable: True; evidence: Five failed attempts before finding the correct REPO_ROOT-based invocation. The agent tried CMS-SUS-16-046.pdf, papers/CMS-SUS-16-046.pdf, and other paths before reading bin/read-paper to understand the tool.)


## Issues

- 59% of Pythia8 shower events failed, and surviving events have kinematically biased distributions. The agent uses N_gen=50,000 as the weight denominator (mathematically correct), but the 20,522 surviving events are not a representative subsample — events where the compressed gluino decay chain (Δm=50 GeV) succeeds are kinematically different from those where it fails. This produces both an overall ~2.9× yield deficit and a distorted S_T^γ shape (bin ratios to reference: 0.20, 0.16, 0.17, 0.38). (severity: major; evidence: Shower log: 20,522/50,000 events succeeded. Report states 'Failed events are dropped; the normalization denominator remains N_gen = 50,000.' Bin-by-bin comparison to reference shows non-uniform ratios, confirming shape distortion beyond a flat efficiency loss.)
- The agent accepted the 59% shower failure rate without attempting diagnostics or mitigation. Standard workarounds include: (1) letting MG5 handle the full decay chain via MadSpin rather than relying on Pythia8's SLHA decay table, (2) adjusting Pythia8's ProcessLevel or TimeShower parameters for compressed spectra, (3) generating the gluino decays at matrix-element level. Any of these could have substantially reduced the failure rate and improved the yield prediction. (severity: major; evidence: The agent states 'likely due to numerical instability in high-multiplicity heavy SUSY cascades' but makes no attempt to investigate further, check Pythia8 error messages, or try alternative configurations.)
- Multiple sleep-and-check cycles during the Pythia8 shower (5+ rounds of sleep 120 + tail), consuming context tokens without advancing the work. (severity: minor; evidence: Session shows at least 5 sequential 'sleep 120 && tail' commands while monitoring shower progress from 6000 to 20522 events.)
