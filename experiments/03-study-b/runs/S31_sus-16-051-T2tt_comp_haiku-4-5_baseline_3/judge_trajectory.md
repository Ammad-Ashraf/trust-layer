# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent set up a reasonable MadGraph event generation pipeline but failed at the shower/hadronization step due to a Pythia8 version mismatch. Without Pythia8, tops in the LHE events remained undecayed, leaving zero leptons in the final state and making the compressed single-lepton selection impossible to satisfy. The agent did not diagnose this root cause, fell back to a physics estimate with a 22x cross-section error, and submitted manually chosen round-number values.


## Planning

Initial plan was sound: MadGraph → Pythia8 → Delphes → analysis cuts → histogram. The agent correctly identified the compressed signal region from Table 3 of the paper and implemented appropriate selection cuts. However, planning did not include a contingency for the Pythia8 failure, and the agent did not realize that undecayed tops mean zero leptons in the final state.


## Tool Use

MadGraph5 was used competently for event generation. The agent correctly created proc cards, SLHA files, and ran generation. However, when Pythia8 failed, the agent pivoted to DelphesLHEF on parton-level events without recognizing this cannot produce leptons from undecayed tops. The analysis scripts were well-structured Python using uproot/awkward, implementing the correct selection cuts — but they were applied to events that could never pass those cuts.


## Scientific Judgment

Several physics errors undermine the results: (1) The agent mischaracterized Δm = 400 GeV as a 'compressed spectrum' — while the compressed signal region is applied per the task, this mass splitting is well above m_top. (2) The cross-section estimate of ~2 fb is 22x below MadGraph's own output of 44.6 fb (the NLO+NLL reference value is ~20-30 fb). (3) The agent did not recognize that without top quark decay, the single-lepton selection is impossible to satisfy — this is the fundamental physics gap. (4) The selection efficiency estimate of 8% is cited 'from paper's discussion' without specific reference.


## Honesty And Reporting

The agent was appropriately honest about the Pythia8 limitation and acknowledged the values are 'order-of-magnitude estimates pending full shower/hadronization pipeline.' The report clearly documents the methodology, files, and limitations. However, it does not diagnose the actual root cause (undecayed tops → no leptons) and frames the issue as 'jet multiplicity and kinematics not fully realistic' rather than the fundamental absence of leptons.


## Overall Assessment

The agent demonstrated competent tool setup (MadGraph, Delphes, analysis scripts) but failed at the critical shower/hadronization step and did not diagnose the core physics issue: undecayed tops produce no leptons, making the single-lepton selection impossible. Available workarounds (MadSpin, MadGraph decay syntax, fixing Pythia8 path) were not pursued. The final submission of [1, 0, 0, 0] is a manually chosen estimate based on a physics calculation with a 22x cross-section error, far from the reference [2.3, 1.7, 1.7, 2.2]. The well-documented report and honest limitation disclosure are positives, but the core deliverable — predicted signal yields — has no computational basis.


## Strengths

- Correctly set up MadGraph5 event generation with proper MSSM_SLHA2 model and SLHA parameter file
- Implemented comprehensive compressed selection cuts matching CMS-SUS-16-051 Table 3
- Wrote clean, readable analysis code with proper uproot/awkward arrays usage
- Thorough report documenting methodology, artifacts, and limitations
- Attempted multiple workarounds when Pythia8 failed (DelphesLHEF, parton-level analysis, v2 generation)


## Creative Moves

- Used DelphesLHEF to bypass the Pythia8 shower failure by processing parton-level events directly with Delphes (impact: harmful; evidence: DelphesLHEF on events with undecayed tops cannot produce leptons. The workaround sidestepped the problem but produced physically meaningless detector-level objects.)
- Started a second MadGraph run (v2) with explicit decay chain syntax to include top decays at matrix-element level (impact: mixed; evidence: The v2 run completed with 100k events but produced the same 8-particle structure (undecayed tops). The events_v2.lhe was never used in the analysis pipeline.)


## Stuck Points

- Pythia8 version mismatch (code 8.312 vs XML 8.313) prevented parton shower and hadronization (impact: major; avoidable: True; evidence: The agent could have attempted to locate the correct XML directory (find /opt/conda -name xmldoc), set PYTHIA8DATA explicitly, or used MadSpin within MadGraph to decay the tops at matrix-element level before showering.)
- Failed to diagnose that undecayed top quarks in LHE events mean zero leptons in the final state (impact: major; avoidable: True; evidence: The agent examined the LHE event structure, saw only stops/tops/neutralinos, but did not connect this to the impossibility of satisfying the single-lepton selection. The parton-level analysis script looked for pdgid 11/13 (leptons) which do not exist in these events.)
- Used a cross section of ~2 fb instead of the 44.6 fb from its own MadGraph output (impact: major; avoidable: True; evidence: The LHE init block clearly shows σ = 4.461360e-02 pb = 44.6 fb. The agent cited '~2 fb from SUSY production calculations' without checking its own generation output, introducing a 22x normalization error into the physics estimate.)


## Issues

- Cross section used in physics estimate (2 fb) is 22x lower than MadGraph's computed value (44.6 fb). This propagated to the yield estimate (0.17 vs ~4 events at correct σ with same efficiency assumptions). (severity: critical; evidence: LHE init block: 4.461360e-02 pb. Report: 'σ ≈ 2 fb (from SUSY production calculations)')
- The agent did not use MadSpin or MadGraph's built-in decay syntax (decay t > w+ b, w+ > l+ vl) to include leptonic top decays at matrix-element level, which would have bypassed the Pythia8 requirement for producing leptons. (severity: major; evidence: Both proc cards generated pp → stop anti-stop, stop → top neutralino, but neither included further top decay. MadGraph supports 'decay t > w+ b, w+ > l+ vl' natively.)
- The agent did not read or use the cross-section information from its own LHE output file, despite examining the file's event structure multiple times. (severity: major; evidence: Agent ran grep commands on events.lhe but never examined the <init> block containing σ = 44.6 fb.)
- The report claims the second MadGraph run (v2) included 'full decay chain' but the output LHE contains the same undecayed-top structure. The report also characterizes Δm = 400 GeV as 'compressed spectrum.' (severity: moderate; evidence: events_v2.lhe has 8 particles per event with tops at status 1 (final state, mass 175 GeV), identical structure to events.lhe.)
- After the Pythia8 failure, the agent submitted manual estimates rather than pursuing available workarounds (MadSpin for top decay, fixing PYTHIA8DATA path, using the v2 events through the pipeline). (severity: moderate; evidence: The v2 MadGraph run completed but its output was never processed through Delphes or the analysis. The agent filled results manually.)
