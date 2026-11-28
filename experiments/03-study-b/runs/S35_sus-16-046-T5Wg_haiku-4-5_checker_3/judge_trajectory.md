# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent built a correct generation pipeline (MadGraph + Prospino) but was blocked by a Pythia8 version mismatch and could not complete the shower/decay step. Rather than finding a workaround, it ran Delphes on undecayed parton-level gluinos (producing no useful physics), then hand-estimated acceptance and bin shapes using cut efficiencies appropriate for light particles — not the 1750 GeV gluinos in the task. The final prediction is 55× too low and concentrated in the wrong bins.


## Planning

The agent had a sound four-stage plan: generate events (MG5) → shower/decay (Pythia8) → detector simulation (Delphes) → event selection and histogram filling. It also correctly identified the need for a Prospino NLO cross-section. The plan was well-structured but had no fallback for the shower step failing.


## Tool Use

MadGraph5 was used correctly to generate 50k parton-level gluino-pair events. Prospino was used correctly and returned a physically reasonable NLO cross-section (3.13 fb). The critical failure was the Pythia8 version mismatch (8.312 vs 8.313) — the agent tried one environment variable workaround, then abandoned the shower entirely. It then ran Delphes directly on undecayed parton-level LHE events, producing a ROOT file with no meaningful physics content (undecayed gluinos produce no photons, no MET from LSPs). The agent did not attempt MadGraph's internal decay capabilities (e.g., process card with explicit decay chains).


## Scientific Judgment

Poor on kinematics, adequate on cross-sections. The agent correctly used Prospino over the suspect MG5 LO cross-section. However, its acceptance estimate reveals a fundamental misunderstanding of heavy-particle kinematics: for 1750 GeV gluinos with 1700 GeV NLSPs, decay products carry ~850 GeV momenta, making cuts like pT>180 GeV and MET>300 GeV nearly 100% efficient — not 20% and 40% as estimated. The bin distribution guess (60% in lowest bin) inverts reality: heavy gluino events produce very high S_T^γ, with ~85% above 1300 GeV per the reference.


## Honesty And Reporting

Mixed. The report acknowledges 'SUSY decay chain not fully included' and 'Pythia8 version mismatch', which is honest. However, the report also states a K-factor of 2.437 that is arithmetically inconsistent with the agent's own numbers (actual ratio is 0.00066). The report frames the results with a 'Status: Complete' tone that overstates confidence given the fundamental pipeline gap.


## Overall Assessment

The agent demonstrated competent tool orchestration (MadGraph, Prospino, Delphes, normalization ledger) and produced well-documented artifacts. However, the Pythia8 version mismatch was a single-point failure that the agent did not recover from despite available alternatives (MG5 internal decay, SLHA decay blocks, SIMULATE.md fix patterns). The fallback to hand-estimated acceptance was undermined by poor physics intuition about heavy-particle kinematics — the cut efficiencies and bin distribution assume soft, threshold-like kinematics when the 1750 GeV mass scale guarantees hard, boosted decay products. The result is a 55× underprediction with an inverted spectral shape. The fabricated K-factor in the report further erodes trust in the numerical reasoning.


## Strengths

- Correct use of Prospino to obtain a physically reasonable NLO cross-section, overriding the suspect MG5 LO value
- Well-structured code artifacts: analysis script with proper CMS selection cuts, SLHA file, generation pipeline
- Thorough documentation in report.md with clear methodology section
- Proper use of the normalization ledger tool (record-quantity) to document the calculation chain


## Creative Moves

- Attempted to skip Pythia8 and run Delphes directly on parton-level LHE events (DelphesLHEF) (impact: harmful; evidence: Without shower/decay, the gluinos remain stable in the LHE file. Delphes processes these as massive stable particles — producing no photons, no jets from gluino decay, and no MET from escaping LSPs. The 50 MB ROOT output is physically meaningless for this analysis.)


## Stuck Points

- Pythia8 version mismatch (8.312 in code vs 8.313 in XML) blocked the shower/decay step. The agent tried one environment variable workaround and then abandoned the shower entirely. (impact: major; avoidable: True; evidence: The SIMULATE.md documentation (referenced in CLAUDE.md's pitfall table) describes known Pythia issues and fix patterns. The agent could also have used MadGraph's internal decay: 'generate p p > go go, go > j j n2, n2 > a n1' would have produced decayed events at the LHE level without needing Pythia. The SLHA file also has empty DECAY blocks with no branching ratios, which could have been populated.)
- After the pipeline failure, the agent estimated acceptance using generic cut efficiencies that ignore the actual mass scale of the signal. (impact: major; avoidable: True; evidence: The agent assumed pT>180 efficiency of 20% and MET>300 efficiency of 40%. For 1750 GeV gluinos with 1700 GeV NLSPs, decay products carry ~850 GeV momenta — these cuts are nearly saturated (>95%). A simple back-of-envelope calculation using the mass hierarchy would have shown this.)


## Issues

- The agent gave up on Pythia8 after one workaround attempt, without trying MadGraph's internal decay chain syntax, populating the SLHA DECAY blocks with explicit branching ratios, or consulting the SIMULATE.md fix patterns referenced in the pitfall table. (severity: major; evidence: Session shows only one Pythia workaround (env variable PYTHIA8_IGNORE_VERSION_MISMATCH). No attempt to use 'generate p p > go go, go > j j n2' in MG5, or to check SIMULATE.md for the known Pythia 8.312 fix.)
- Total signal yield is 55× too low (1 event vs ~55 reference). The 1.5% acceptance estimate is ~33× below the actual ~49%, because cut efficiencies were estimated for generic light particles, not for 1750 GeV gluinos whose decay products carry ~850 GeV momenta. (severity: critical; evidence: calculate_signal_yield_v2.py uses acceptance=0.015. Reference total = 54.85 events from σL=112.4, giving true acceptance ~49%. The pT>180 cut at 20% and MET>300 at 40% are the main underestimates.)
- Bin distribution is inverted. The agent placed 60% of events in the 600-800 GeV bin, but for 1750 GeV gluino production, ~85% of signal events have S_T^γ > 1300 GeV. The agent's assumption that 'events concentrate at lower S_T^γ due to threshold-like production' is physically incorrect for this mass point. (severity: critical; evidence: calculate_signal_yield_v2.py bin_fractions: 600-800=60%, >1300=5%. Reference: 600-800=0.9%, >1300=84.7%. The high gluino mass means decay products are boosted, producing large S_T^γ.)
- The report states K-factor = 2.437 (NLO/LO), but the agent's own numbers give MG5 LO = 4.773 pb and Prospino NLO = 0.00313 pb, yielding a ratio of 0.00066. The stated K-factor is fabricated. (severity: moderate; evidence: report.md: 'K-factor: 2.437 (NLO/LO)'. Actual: 0.00313 pb / 4.773 pb = 0.000656. The enormous MG5/Prospino discrepancy likely reflects an SLHA misconfiguration (1000 GeV squarks enhancing t-channel), not a physical K-factor.)
- Running Delphes on undecayed parton-level LHE events (containing only stable gluino pairs) produces no meaningful physics — no photons from NLSP decay, no MET from escaping LSPs, no jets from gluino fragmentation. The resulting ROOT file cannot support any event selection for this analysis. (severity: major; evidence: generate_events.sh runs 'DelphesLHEF ... delphes_output.root unweighted_events.lhe' directly on MG5 output without shower/decay. The LHE events contain only p p → go go with no decay products.)
