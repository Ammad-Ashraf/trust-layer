# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent executed a complete, well-structured simulation chain (MG5→Prospino→Pythia8→Delphes→analysis) for TChiWZ_550_200 signal prediction. It recovered well from two significant technical obstacles (MG5 param card misconfiguration and pyhepmc segfault). The main physics shortcoming is a too-narrow Z mass window (±5 GeV instead of ±15 GeV), which likely costs ~30-40% of signal yield. Total yield is ~60% of reference.


## Planning

Strong task decomposition. The agent identified the full pipeline early: (1) set up SLHA param card, (2) Prospino NLO cross section, (3) MG5 event generation, (4) Pythia8 shower, (5) Delphes detector sim, (6) analysis with VZ cuts. It read the paper to extract the VZ signal region definition, correctly identifying the key cuts (on-Z, ≥2 jets, b-veto, mjj, MT2, MET bins). The pipeline was executed in logical order with cross-checks at each stage.


## Tool Use

Effective use of the simulation stack (MG5, Prospino, Pythia8, Delphes) and the bin/run-analysis framework. The agent correctly used bin/prospino for NLO normalization (running both charge channels separately and summing), configured MG5 with the MSSM_SLHA2 model, and set up Pythia8 with SLHA decay tables. Some time was spent debugging pyhepmc API (from_hepevt segfault), but the agent found a working manual GenEvent construction approach. The agent ran the analysis twice to verify reproducibility.


## Scientific Judgment

Mostly sound. The agent correctly identified that NLO normalization was needed and computed it via Prospino. It properly set up the MSSM mass spectrum with decoupled squarks/sleptons and the correct chargino/neutralino masses. The VZ region implementation covers most cuts correctly (OSSF, b-veto, mjj closest-dphi pair, MT2, dphi(jet,MET)). However, the Z mass window was set to 86-96 GeV (±5 GeV around 91 GeV) rather than the standard CMS on-Z selection of |m_ℓℓ - m_Z| < 15 GeV (76.2-106.2 GeV). This is a significant cut that loses Z→ℓℓ events in the tails of the Breit-Wigner plus detector resolution smearing. The report's deviation section is honest but does not flag this discrepancy.


## Honesty And Reporting

Good. The report clearly documents six deviations from the paper's methodology (Delphes vs full sim, NLO vs NLO+NLL, lepton isolation, b-tag threshold, spin correlations, MT2 implementation). The cutflow is documented with event counts at each stage. However, the narrow Z mass window is not flagged as a deviation, suggesting the agent believed 86-96 GeV was correct.


## Overall Assessment

A strong agent run that executed a complete, legitimate simulation pipeline from scratch. The agent demonstrated good technical resilience, recovering from both the MG5 param card misconfiguration and the pyhepmc segfault without losing significant time. The main shortcoming is a too-narrow Z mass window (86-96 GeV vs 76-106 GeV), which is a physics specification error that likely explains a substantial portion of the ~40% yield deficit. The remaining deficit is attributable to known fast-sim vs full-sim differences. All submitted values are fully traceable to the agent's computation, the report is well-documented, and the analysis is reproducible.


## Strengths

- Complete end-to-end simulation chain from scratch — not a shortcut or extraction approach
- Proper NLO normalization via Prospino with both charge channels computed separately
- Good recovery from MG5 param card failure (detected wrong masses from cross-section discrepancy, re-generated with corrected card)
- Good recovery from pyhepmc segfault by switching to manual GenEvent construction
- Reproducible analysis (ran twice, identical output)
- Well-structured report documenting the full pipeline and known approximations


## Creative Moves

- Detected the MG5 param card failure by noticing the LO cross section (0.9045 pb) was far too high for 550 GeV sparticles, then traced it to MG5 ignoring the SLHA and using default masses. Fixed by copying the restrict_default.dat template and modifying masses in-place. (impact: helpful; evidence: Session shows: MG5 LO xsec 0.9045 pb → agent checks param_card.dat → finds default masses → creates modified restrict_default.dat → re-runs → gets 0.01372 pb (correct order of magnitude))
- When pyhepmc from_hepevt segfaulted on events with ~1800 particles, the agent wrote a minimal pythia_to_hepmc_simple function that constructs GenEvents with only beam (status 4) and final-state (status 1) particles, sufficient for Delphes input. (impact: helpful; evidence: Session shows segfault at 'from_hepevt' with 1814 particles, then switch to manual vertex+particle construction that works for all 50k events)


## Stuck Points

- Spent ~10 tool calls exploring the pyhepmc API (from_hepevt, GenEvent construction, io.WriterAscii) before finding a working approach for HepMC3 output from Pythia8. (impact: minor; avoidable: True; evidence: Multiple python3 -c test snippets exploring pyhepmc API, AttributeError on add_particle_out, segfault on from_hepevt before settling on the manual approach)
- Initial MG5 param card approach used 'set param_card' commands which were silently ignored, leading to generation with wrong masses. Required a full re-generation of 50k events. (impact: moderate; avoidable: True; evidence: First run produced LO xsec 0.9045 pb (default light masses); agent detected this, diagnosed the param_card issue, and re-ran with the corrected approach)


## Issues

- The Z mass window was set to 86-96 GeV (±5 GeV around m_Z) instead of the standard CMS on-Z selection of |m_ℓℓ - m_Z| < 15 GeV (76.2-106.2 GeV). This narrower window loses Z→ℓℓ events in the Breit-Wigner tails and detector-smeared tails, likely accounting for a significant fraction of the ~40% yield deficit relative to the reference. (severity: moderate; evidence: analysis.py lines: MZ_LO = 86.0, MZ_HI = 96.0; report states '86 < m_ℓℓ < 96 GeV' as the on-Z requirement. The standard CMS on-Z definition is |m_ℓℓ - 91.2| < 15 GeV.)
- The analysis uses NLO (Prospino 2.1) rather than NLO+NLL cross sections used by CMS. The report acknowledges this as a ~5% effect. Additionally, the Delphes fast-sim with no pileup systematically differs from the CMS full simulation, contributing to the overall ~40% deficit. (severity: minor; evidence: Report deviation #2: 'We use Prospino 2.1 at NLO (without resummation). The difference is typically ≲ 5%.' Deviation #1: 'We use Delphes fast simulation with the CMS card, which approximates detector resolution and efficiency but does not include pileup.')
