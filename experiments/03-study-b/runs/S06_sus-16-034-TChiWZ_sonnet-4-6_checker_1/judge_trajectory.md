# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent executed a full MadGraph→Pythia8→Delphes→analysis chain, correctly used Prospino NLO cross sections for both charge channels, and diagnosed/fixed three non-trivial technical bugs (MG5 particle names, missing SLHA decay BRs, HepMC3 vertex counter). Final yields are ~3–4× low, primarily due to limited statistics (10k of 50k events processed), possible analysis cut tightness, and use of the generic Delphes CMS card.


## Planning

Good top-level plan: generate events, shower, simulate detector, analyze. The agent parallelized Prospino and MadGraph runs and wrote the analysis script while waiting for the shower. Properly identified the need for both χ̃⁺₁χ̃⁰₂ and χ̃⁻₁χ̃⁰₂ Prospino calculations. Did not plan for the OOM issue but adapted when it arose.


## Tool Use

Strong adaptation to tool failures. Debugged the read-paper tool path, iterated on MG5 proc_card syntax (particle names, LHAPDF removal), read Delphes C++ source to diagnose the HepMC3 vertex counter bug, and used Python one-liners to verify decay chains in shower output. Prospino was run correctly with appropriate ipart1/ipart2 flags. The bin/record-quantity ledger tool was used thoroughly.


## Scientific Judgment

Correct physics choices throughout: NLO normalization via Prospino rather than MG5 LO, combined both charge channels, decoupled all non-relevant sparticles at 3 TeV, forced 100% BR for χ̃⁰₂→Zχ̃⁰₁ and χ̃⁺₁→W⁺χ̃⁰₁ (physically correct for this simplified model). The VZ signal region cuts follow the paper specification. The agent correctly noted the PDF mismatch (NNPDF vs CTEQ6) and chose the Prospino NLO value. One weakness: the MT2 calculation used a symmetric bisection approximation rather than a proper MT2 library, which may have affected cut efficiency.


## Honesty And Reporting

Excellent. The report explicitly lists all possible issues: limited statistics (10k of 50k events), per-bin statistical uncertainties (58% for the lowest bin), the HepMC3 vertex fix, the PDF mismatch, and the missing BR lines. The agent did not overclaim accuracy and flagged the low-statistics concern prominently.


## Overall Assessment

A competent and honest simulation run that completed the full MadGraph→Pythia8→Delphes→analysis pipeline with correct NLO normalization. The agent showed strong debugging skills, fixing three non-trivial technical issues independently. The main weakness is quantitative: yields are ~3–4× low relative to the reference, likely a combination of low statistics (35 events passing from 10k), possible cut over-tightness, and the generic Delphes CMS card. The agent's reporting was exemplary — all limitations were flagged transparently with quantified uncertainties.


## Strengths

- Diagnosed and fixed three distinct technical bugs (MG5 names, missing SLHA decay BRs, HepMC3 vertex counter) without external help
- Correct NLO normalization using both Prospino charge channels (8.52 + 3.35 = 11.87 fb)
- Thorough ledger record-keeping with formula verification (1.49 total cross-checked)
- Transparent reporting of statistical limitations and technical workarounds


## Creative Moves

- Read the Delphes C++ source (DelphesHepMC3Reader.cc) to diagnose why the ROOT output had 0 entries, identified the fVertexCounter==-1 requirement, and fixed the HepMC3 E-line from nVertices=1 to nVertices=0 (impact: helpful; evidence: grep/sed on DelphesHepMC3Reader.cc lines 387-460 showing EventReady() logic; sed fix on E-lines; subsequent Delphes run producing 10k entries)
- Patched the LHE header SLHA section to inject explicit χ̃⁰₂ and χ̃⁺₁ decay channels when MG5-generated LHE had no BR lines (impact: helpful; evidence: Test with 100 events showed chi01 appearing 2×/event and electrons/muons from Z decays after the fix)
- Extracted 10k-event subset from 50k HepMC file when Delphes OOM'd on the full sample (impact: mixed; evidence: Full 50k sample killed (exit 137); 10k subset processed successfully, but this reduced statistical power by 5×)


## Stuck Points

- Multiple MadGraph5 proc_card iterations: wrong particle names (c1+ vs x1+), LHAPDF not available, parameter setting in launch block (impact: moderate; avoidable: True; evidence: Three full proc_card rewrites and rm -rf cycles before successful generation)
- Pythia8 XML directory path and version mismatch required multiple attempts to resolve (impact: minor; avoidable: True; evidence: find commands for Index.xml, testing with python3 -c imports before finding correct path)
- Full 50k-event Delphes run killed by OOM (exit 137), requiring fallback to 10k events and losing 80% of generated statistics (impact: major; avoidable: True; evidence: free -h showed exhausted swap; 10k events yielded only 35 passing events (3 in lowest MET bin))


## Issues

- Final yields are systematically ~3–4× below the CMS reference. While the normalization formula itself is correct (σ_NLO × L × n_bin/N_analyzed), the selection efficiency of 0.35% is likely too low, possibly due to tight analysis cuts, approximate MT2 calculation, or generic Delphes card effects. (severity: moderate; evidence: Submitted total 1.49 events vs reference total 5.41 events (ratio ~0.28). The 86–96 GeV on-Z window is correct per the paper, but MT2 is computed via symmetric bisection approximation rather than a proper library.)
- Only 10k of 50k generated events were processed through Delphes due to OOM. The agent could have attempted batched processing (e.g., 10k at a time, merging ROOT outputs) to recover more statistics. (severity: minor; evidence: 50k HepMC events available (2.8 GB), but only first 10k extracted and simulated. No attempt at batch processing.)
