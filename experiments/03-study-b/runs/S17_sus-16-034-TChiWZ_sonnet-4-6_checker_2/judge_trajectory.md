# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent executed a complete recast pipeline (SLHA→MadGraph→Pythia8→Delphes→ROOT analysis) for TChiWZ 550/200, correctly diagnosing and resolving a non-trivial physics issue (vanishing bino-wino-Z coupling) and multiple toolchain format problems. Final yield is 3.455 events vs 5.41 reference — systematically low but physically reasonable given Delphes approximations.


## Planning

The agent followed a natural simulation chain without explicit upfront planning but adapted well as issues arose. It read the paper, identified the VZ signal region, set up the SLHA spectrum, and proceeded through generation, showering, detector sim, and analysis. The agent wrote the analysis code while Delphes ran in the background — good parallelism.


## Tool Use

Strong tool use overall. The agent navigated MadGraph, Prospino, Pythia8, Delphes, uproot, and the ColliderBench CLI tools (bin/record-quantity, bin/read-paper, bin/simulate). It debugged HepMC2 vs HepMC3 format incompatibilities, ran Delphes in the background when foreground timeouts hit, and used small test batches (1000 events) to validate the pipeline before committing to the full 50k run.


## Scientific Judgment

Excellent identification of the bino-wino mixing matrix problem: the χ̃⁰₂→Z χ̃⁰₁ vertex vanishes for pure eigenstates in MadGraph's matrix element, so the agent correctly switched to production-only generation with Pythia handling decays via SLHA tables. Used Prospino NLO cross-section (19.8 fb) rather than the MadGraph LO value (20.28 fb). Verified particle content in HepMC events (confirmed Z/W decay and χ̃⁰₁ stability). The VZ SR cut implementation is detailed and mostly faithful to the paper, including MT2(ll), m_jj, and b-veto. The on-Z window (86–96 GeV) is tighter than the typical 76–106 GeV used by some CMS analyses, which could contribute to the yield deficit.


## Honesty And Reporting

The report.md explicitly documents six deviations from the CMS analysis (LO PDF, Delphes vs GEANT4, MET resolution, JEC, trigger, N_gen). Statistical uncertainty is quoted (6.4%). No overclaiming of agreement with CMS results.


## Overall Assessment

A competent recast with a complete and traceable simulation pipeline. The agent's strongest moment was diagnosing the bino-wino-Z coupling problem — a subtle MSSM physics issue that many agents would miss or mishandle. The systematic yield deficit (~36% below reference) is plausibly explained by the combination of Delphes detector approximation, the narrower-than-specified on-Z window, no pileup modeling, and simplified trigger treatment. The toolchain debugging (MadGraph iterations, HepMC format) consumed significant context but was ultimately resolved. The final artifacts are well-documented and reproducible.


## Strengths

- Correctly diagnosed the vanishing bino-wino-Z coupling and adapted the generation strategy
- Self-consistent normalization: σ×L×ε = histogram sum verified
- Fixed the overflow bin bug (MET>350 capped at 450) before final submission
- Parallelized work: wrote analysis code while Delphes ran in background
- Thorough report documenting methodology and known approximations


## Creative Moves

- Switching from MadGraph explicit decays to production-only generation + Pythia SLHA decay tables to work around the vanishing tree-level bino-wino-Z coupling (impact: helpful; evidence: MadGraph v2 run gave zero cross-section warning for chi02→Z chi01 decay. Agent recognized the MSSM coupling structure (proportional to higgsino content) and moved decays to Pythia, which enforces them from the SLHA table regardless of coupling.)
- Using a 1000-event test batch to debug the HepMC format issue before running full Delphes (impact: helpful; evidence: First Delphes run on full HepMC3-format file produced 0 events in ROOT. Agent extracted 1000 events, tested with both DelphesHepMC3 and DelphesHepMC2, identified the format mismatch, rewrote the shower script to output HepMC2, and confirmed events appeared in ROOT before committing to the full run.)


## Stuck Points

- Four iterations of the MadGraph process card (v1–v4) due to SLHA import issues, default mass conflicts, and mixing matrix problems (impact: moderate; avoidable: True; evidence: v1 used import_model with SLHA but masses weren't applied; v2 used updated param_card but had wrong mixing; v3 added explicit decays but coupling was zero; v4 finally used production-only. Could have started with production-only approach given the simplified model.)
- HepMC3 vs HepMC2 format confusion caused Delphes to produce empty ROOT files (impact: moderate; avoidable: True; evidence: pyhepmc defaults to HepMC3 ASCII format, but the agent initially called DelphesHepMC3 which failed silently, then discovered DelphesHepMC2 reader was needed after switching to HepMC2 output format. The first full Delphes run was wasted.)


## Issues

- The on-Z mass window (86–96 GeV, width 10 GeV) is narrower than the typical CMS dilepton mass window for on-Z selections. CMS-SUS-16-034 specifies |m_ll − m_Z| < 15 GeV (i.e., 76.3–106.3 GeV). This tighter window would reduce signal acceptance. (severity: minor; evidence: analysis_VZ.py line implementing '86 < m_ll < 96 GeV' vs paper's stated |m_ll − m_Z| < 15 GeV window. The report.md lists the cut as '86 < m_ll < 96 GeV' without noting this differs from the paper's definition.)
- Multiple Delphes runs were attempted and killed before the agent ran it in the background, wasting ~4 minutes of wall time. (severity: minor; evidence: Three foreground Delphes attempts hit the 2-minute timeout or were OOM-killed before the agent switched to background execution.)
