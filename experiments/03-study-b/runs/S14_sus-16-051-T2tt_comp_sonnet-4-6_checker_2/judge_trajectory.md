# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent executed the full MadGraph5→Pythia8→Delphes→analysis chain for the CMS-SUS-16-051 compressed T2tt signal region. It encountered and resolved three substantive physics bugs (HepMC beam-particle status codes, neutralino visibility to Delphes, missing parton info for b-tagging) through principled debugging. Final yields are ~30–58% below reference, primarily due to LO-only ISR modeling in the compressed regime.


## Planning

Good top-down decomposition: paper reading → Prospino cross section → MadGraph5 generation → Pythia8 showering → Delphes detector sim → analysis selection → normalization. The agent correctly identified the CMS-SUS-16-051 compressed signal region requirements (Table 3) and planned the full chain before starting. It also recorded quantities (cross section, luminosity, branching fraction) in the ledger as it went.


## Tool Use

Generally competent. The agent navigated read-paper path issues, the bin/run-analysis harness requirements (datasets.yaml format, analysis.py referencing it), and Prospino CLI flags through iterative exploration. It solved the Delphes OOM by splitting HepMC into 10k-event chunks. Some time was spent on false starts with the launch scripts and conda paths, but nothing egregious.


## Scientific Judgment

Strong on three key physics points: (1) correctly identified that neutralinos must be excluded from HepMC output so Delphes computes MET from momentum imbalance rather than treating χ̃₁⁰ as a neutral hadron; (2) correctly diagnosed that zero b-tagged jets meant parton-level flavor info was missing for Delphes JetFlavorAssociation, and fixed by writing primary b/c quarks with HepMC status=3; (3) correctly noted in the report that LO generation with shower-only ISR is a major limitation for the compressed selection (Njet≥5, leading jet not b-tagged), which requires ISR recoil. The agent did not attempt MLM matching or other ISR improvements, which would have been difficult but could have improved results significantly.


## Honesty And Reporting

The report is thorough and honest. It explicitly lists generator-level (LO only), b-tagging (parametrized efficiency), fast-sim, and sample-size limitations. The 'Possible Issues' section correctly flags ISR sensitivity and the lack of MG5+MLM matching as the dominant systematic concern for the compressed region. No overclaiming.


## Overall Assessment

A competent and honest run. The agent built the full simulation chain from scratch, resolved three non-trivial physics bugs through principled debugging, and produced traceable results with correct normalization. The ~30–58% deficit relative to reference is dominated by the LO-only ISR treatment in a selection region that requires high jet multiplicity from initial-state radiation — a known limitation the agent correctly identified but did not attempt to mitigate via MLM matching. The final artifacts (analysis.py, report.md, datasets.yaml, ledger.yaml) are well-organized and would allow another agent to continue or improve the analysis.


## Strengths

- Full end-to-end simulation chain from scratch — MadGraph5, Pythia8, Delphes, custom analysis
- Correct physics debugging of three non-trivial issues (beam status, neutralino visibility, parton b-tagging)
- Proper NLO cross-section normalization via Prospino rather than using the LO MadGraph value
- Honest and detailed reporting of known limitations
- Good recovery from Delphes OOM via chunked processing


## Creative Moves

- Excluded χ̃₁⁰ (PID 1000022) from HepMC output entirely so Delphes reconstructs MET purely from visible-particle momentum imbalance, rather than trying to configure Delphes to treat it as invisible. (impact: helpful; evidence: Session shows MET>250 jumped from ~low% to ~60% of events after this fix, consistent with a 800/400 GeV mass splitting.)
- Wrote primary b/c quarks with HepMC status=3 to provide parton info for Delphes JetFlavorAssociation, enabling b-tagging. (impact: helpful; evidence: B-tagged jet fraction went from ~0% to ~30%, and events with ≥1 b-tag went from ~4% to ~87%.)
- Split 50k-event HepMC file into 5×10k chunks to avoid Delphes OOM kill. (impact: helpful; evidence: All 5 chunks processed successfully after the split, producing ~33KB ROOT files each.)


## Stuck Points

- Multiple iterations debugging the read-paper tool path — the agent tried several path variations before realizing the tool needed the ColliderBench Python module invocation. (impact: minor; avoidable: True; evidence: Five failed read-paper attempts before finding the correct module path.)
- The YAML results file update logic initially tried to replace 'null' placeholders that had already been overwritten by a previous (broken) run, requiring manual edit. (impact: minor; avoidable: True; evidence: Agent had to manually edit histogram_T2tt_comp.yaml after analysis.py's regex-based replacement failed on non-null values.)


## Issues

- LO matrix element generation with ISR produced only by Pythia8 shower significantly underestimates event yields in the compressed selection region, which requires high ISR jet multiplicity (Njet≥5). CMS uses MLM-matched samples with explicit ISR jets for this topology. The agent acknowledged this limitation but did not attempt matching. (severity: moderate; evidence: Submitted total yield 5.39 vs reference 7.9 (32% low). The compressed selection's Njet≥5 and leading-jet-not-b-tagged requirements are strongly ISR-dependent. The agent's report explicitly flags this: 'ISR radiation comes entirely from Pythia8's initial-state shower. CMS often uses dedicated MG5+MLM matched samples.')
- The agent did not explore whether MadGraph5 could generate additional ISR jets at matrix-element level (e.g., p p > t1 t1~ j, p p > t1 t1~ j j) with MLM matching, which would have been the standard CMS approach for the compressed region. (severity: minor; evidence: The proc_card uses only 'generate p p > t1 t1~' without additional jet radiation. MLM matching setup was not attempted.)
- The agent's report transparently identifies all major systematic limitations and correctly flags ISR modeling as the dominant concern. This is a positive finding. (severity: minor; evidence: Report 'Key systematic considerations' and 'Possible Issues' sections enumerate LO-only generation, Delphes parametrized b-tagging, fast-sim limitations, and ISR sensitivity.)
