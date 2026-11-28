# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent completed a full end-to-end SUSY signal simulation (MadGraph→Pythia8→Delphes→analysis) for the CMS-SUS-16-034 VZ signal region, overcoming substantial technical obstacles with MadGraph TTY requirements, SLHA format issues, and Pythia8 version mismatches. The final values systematically undershoot the reference at high MET, consistent with missing NLL normalization and trigger corrections, both of which the agent honestly documented.


## Planning

Strong initial planning: the agent read the task, identified the full simulation chain, checked available tools, and read the paper before writing any code. It correctly diagnosed the wino-bino coupling zero issue (χ̃⁰₂→Zχ̃⁰₁ tree-level width vanishes in pure states) early and separated MadGraph production from Pythia8 decays—a non-trivial physics insight that shaped the entire pipeline.


## Tool Use

The agent navigated a complex toolchain (MadGraph5, Pythia8, Delphes, Prospino, uproot, awkward-array, mt2) with considerable persistence. It installed the missing mt2 package, found the correct Pythia8 xmldoc path, and rewrote the analysis to pass the vectorization preflight check. Tool debugging consumed substantial context but ultimately succeeded.


## Scientific Judgment

Good physics reasoning throughout. The agent correctly identified the wino-bino coupling zero requiring production-only MadGraph + Pythia8 decays, used Prospino K-factors rather than relying on LO alone, applied all 11 VZ signal-region cuts, and computed MT2(ℓℓ) using a proper library. The documented deviations (no NLL, no trigger efficiency, Delphes vs full sim, no charged-track veto) are accurate and explain the systematic deficit. The K-factor application (MG5 total LO × Prospino K) is a standard approximation.


## Honesty And Reporting

Excellent. The report.md explicitly lists six deviations from the paper's methodology, with physically grounded estimates of their impact. The agent does not overclaim agreement and provides a clear cutflow table. The artifacts are well-organized and would allow another agent to reproduce or extend the work.


## Overall Assessment

A strong run that completed the full simulation chain from matrix-element generation through detector simulation and analysis. The agent demonstrated solid physics understanding—particularly in handling the wino-bino coupling zero—and good engineering persistence in overcoming toolchain issues. The systematic yield deficit (23–32% at high MET) is well-explained by documented approximations, primarily the missing NLL cross-section correction and Delphes vs full simulation differences. The first bin agrees within 3%. The run produced clean, well-documented artifacts suitable for follow-up work.


## Strengths

- Complete end-to-end MC simulation chain with proper NLO normalization
- Correct identification and handling of the wino-bino coupling zero physics issue
- Thorough signal-region implementation with all 11 cuts including MT2(ℓℓ) and m_jj
- Honest and detailed documentation of approximations and their expected impact
- Clean artifact organization: SLHA files, analysis code, datasets.yaml, report.md all present


## Creative Moves

- Separated MadGraph production from Pythia8 forced decays to handle the vanishing χ̃⁰₂→Zχ̃⁰₁ tree-level coupling in the pure wino-bino limit (impact: helpful; evidence: Session logs show the agent recognized the coupling issue early: 'in the pure wino-bino limit (N₁₁=1, N₂₂=1), both χ̃⁺₁→Wχ̃⁰₁ and χ̃⁰₂→Zχ̃⁰₁ tree-level vertices vanish.' Created a separate Pythia SLHA with explicit DECAY blocks forcing 100% BR.)
- Built a comprehensive Pythia8 SLHA by programmatically modifying the MG5 default MSSM param card and adding DECAY blocks, after earlier minimal SLHA files caused NaN coupling errors (impact: helpful; evidence: Multiple iterations on SLHA files: first attempt used wrong BLOCK DECAY format, second was missing SUSY blocks causing NaN couplings, final version built from MG5 default card with mass modifications and explicit DECAY entries.)


## Stuck Points

- MadGraph5 generate_events required a TTY, causing multiple failed attempts before the agent found a working invocation using Python's subprocess with pty/script workarounds (impact: moderate; avoidable: False; evidence: ~15 tool calls spent on MadGraph TTY issue, including examining MadEvent source code, trying various flags (-f, --force), pty wrapping, and script-based fake terminal before finding a working approach.)
- SLHA file format errors required three iterations: wrong BLOCK DECAY syntax, missing Yukawa/VCKM blocks, and missing GAUGE block for Pythia8 (impact: minor; avoidable: True; evidence: Agent first wrote 'BLOCK DECAY' instead of 'DECAY', then produced a minimal SLHA missing blocks that MG5 and Pythia8 needed. Could have started from the default param card modification approach used in the final iteration.)
- Paper PDF location: agent couldn't find the paper for several attempts before correctly using the read-paper tool with REPO_ROOT (impact: minor; avoidable: True; evidence: Three failed read-paper attempts with wrong paths before finding the correct invocation.)


## Issues

- Missing NLL resummation on top of Prospino NLO cross section. The paper uses NLO+NLL cross sections from the LHC SUSY Cross Section Working Group, while the agent uses only NLO. At m=550 GeV, NLL adds ~10–15% to the total cross section, contributing to the systematic yield deficit. (severity: moderate; evidence: Report.md deviation #2: 'This analysis uses Prospino 2.1 NLO (no soft-gluon NLL resummation). The NLL correction at 550 GeV would increase the cross section by roughly 10–15%.' The agent was aware but Prospino doesn't provide NLL.)
- No trigger efficiency correction applied. The paper applies 90–96% trigger efficiency weights, effectively reducing yields by 4–10%. However, since the agent's yields are already low, this correction would have further decreased them—the net effect depends on whether the Delphes efficiency is already lower than the paper's corrected efficiency. (severity: minor; evidence: Report.md deviation #4: 'The paper applies trigger efficiency corrections of 90–96%. This analysis does not apply explicit trigger weights (effectively assumes 100% trigger efficiency).')
- The agent proactively documented all six deviations from the paper methodology with estimated magnitudes, enabling downstream assessment of systematic uncertainties. (severity: minor; evidence: Report.md 'Deviations from Paper' section lists: Delphes vs GEANT4, NLO vs NLO+NLL, missing charged-track veto, missing trigger efficiency, Delphes vs mini-isolation, and the coupling zero handling.)
