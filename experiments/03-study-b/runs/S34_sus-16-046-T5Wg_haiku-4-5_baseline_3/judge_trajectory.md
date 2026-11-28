# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent built a complete MG5→Pythia8→Delphes→analysis pipeline and correctly implemented the CMS-SUS-16-046 event selection. However, it failed to ensure SUSY decay chains were applied: the LHE file contained only bare gluino pairs, Pythia8 showering either failed or was bypassed, and Delphes was run directly on undecayed LHE events. The agent correctly diagnosed the root cause (no photons because no decays) but submitted zeros rather than fixing the pipeline.


## Planning

Good initial decomposition: read paper → create SLHA → generate events → shower → detector sim → analysis → fill YAML. The agent identified the right physics (T5Wg decay chain, selection cuts from Table 1, STgamma definition). However, the plan did not include validation checkpoints between pipeline stages—the agent never verified that decay products appeared in the showered events before proceeding to Delphes.


## Tool Use

The agent used MG5, Pythia8, Delphes, and uproot/awkward competently in terms of invocation syntax. It created proper SLHA files, process cards, and analysis scripts. However, when Pythia8 showering encountered problems (the HepMC output may not have been produced), the agent fell back to running DelphesLHEF directly on the raw LHE file—effectively skipping the shower/decay step entirely. This was the fatal shortcut.


## Scientific Judgment

Mixed. The agent correctly understood the T5Wg signal model, the decay chain (gluino → qq + neutralino/chargino, neutralino → photon + gravitino), and the analysis cuts. It correctly identified that the LHE file contained only production-level gluinos without decay products. However, it did not act on this diagnosis—it knew the pipeline was broken but submitted zeros anyway, rather than fixing MG5 to include decay chains in the process definition or debugging Pythia8's SLHA decay handling.


## Honesty And Reporting

Excellent transparency. The report.md explicitly documents the zero-photon problem, provides root cause analysis, and suggests concrete fixes. The agent did not inflate or fabricate results. It correctly attributed the zeros to a simulation pipeline issue rather than claiming the physics signal is small.


## Overall Assessment

The agent demonstrated solid HEP analysis knowledge and built a structurally correct simulation pipeline, but critically failed to ensure SUSY decay chains were applied to the generated events. When Pythia8 showering did not produce usable output, the agent bypassed it by running Delphes directly on undecayed LHE events—guaranteeing zero reconstructed photons and zero signal yields. The agent correctly diagnosed the problem and documented it thoroughly, but did not attempt any of its own suggested fixes, constituting premature surrender on the core physics task. The result is an all-zero histogram against reference yields of 0.49–46.48 events.


## Strengths

- Correct implementation of all CMS-SUS-16-046 event selection cuts (photon pT, eta, MET, MT, STgamma binning)
- Proper SLHA file construction with correct mass spectrum for T5Wg_1750_1700
- Thorough diagnosis of the decay chain failure with concrete suggested fixes
- Honest reporting of zero yields with clear technical explanation
- Well-structured artifacts (analysis.py, report.md, SLHA, process cards) that another agent could pick up and fix


## Creative Moves

- Fell back to DelphesLHEF when Pythia8 HepMC output was unavailable, keeping the pipeline moving (impact: harmful; evidence: Running Delphes directly on the undecayed LHE file guaranteed zero photons. This preserved pipeline continuity but produced physically meaningless results.)


## Stuck Points

- Pythia8 showering failed or did not produce a usable HepMC file. The agent created a v2 shower script but ultimately bypassed Pythia8 entirely by running DelphesLHEF on the raw LHE. (impact: major; avoidable: True; evidence: Session shows 'shower_pythia8.py' and 'shower_pythia8_v2.py' were created, but no HepMC file appears in the final file listing. The agent ran 'DelphesLHEF ... signal_T5Wg.lhe' directly.)
- MG5 process definition used bare gluino pair production (p p > go go~) without decay chains. The agent could have used MG5's decay syntax (e.g., 'generate p p > go go~, go > ... ') to include decays at matrix-element level. (impact: major; avoidable: True; evidence: LHE file inspection showed only gluino production vertices. Agent noted 'Use MadGraph decay_product syntax to include decay chains' as a future fix but did not implement it.)


## Issues

- Agent correctly diagnosed that gluino decays were missing (no photons in generated sample) but submitted all-zero results rather than fixing the pipeline. It had time and tools to either regenerate with MG5 decay syntax or debug Pythia8 SLHA reading. (severity: critical; evidence: Report states 'Zero yields due to absence of photons in generated sample' and lists three concrete fixes, none of which were attempted.)
- When Pythia8 failed to apply SUSY decays, the agent could have: (1) used MG5's built-in decay chain syntax, (2) used MadSpin for the decays, (3) debugged Pythia8's SLHA reading with diagnostic flags, or (4) generated the full process including decays at matrix-element level in MG5. (severity: major; evidence: Agent listed these as 'Solution (for future implementation)' in report.md but did not try any of them in the session.)
- The agent's report.md is unusually transparent about the failure mode, providing detailed root cause analysis and actionable fixes. This is a positive quality despite the failed physics result. (severity: minor; evidence: Report includes 'Technical Issues & Lessons Learned' section with root cause, investigation steps, and three concrete solutions.)
