# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent completed a full end-to-end LO+PS+Delphes simulation of T2tt (stop 800, neutralino 400) with CMS-SUS-16-051 compressed selection. It encountered and resolved five technical obstacles — MG5 mass misconfiguration, Pythia version mismatch, HepMC3 vertex format, Delphes OOM, and critically the missing parton history for b-tagging. Final yields are ~29% below reference, consistent with LO+fast-sim limitations.


## Planning

Strong task decomposition: read the paper first, obtained the NLO cross section from Prospino before event generation, set up the full chain in logical order (MG5→Pythia→Delphes→analysis), recorded quantities in the ledger as they were produced. The agent correctly identified the compressed signal region (not the standard one) as the target from Table 3.


## Tool Use

Effective use of the full simulation toolchain. Used bin/prospino for NLO cross section, MG5 for event generation, Pythia8 via Python bindings, Delphes CLI, and uproot/awkward for ROOT analysis. Adapted to tool constraints: split HepMC3 into chunks when Delphes OOM'd, used hadd to merge ROOT files, debugged pyhepmc vertex API. Used bin/record-quantity and bin/run-analysis correctly after learning their interfaces.


## Scientific Judgment

Good physics reasoning throughout. Caught the 1.256 pb cross section anomaly (expected ~16-20 fb for 800 GeV stops) which revealed the mass misconfiguration. Correctly diagnosed the b-tagging crisis: 6% b-tag rate was unphysical and traced to missing parton history in HepMC3, not a cut logic error. Used Prospino NLO for normalization rather than MG5 LO. Applied the correct compressed-region Δφ threshold (0.5, not 0.8). Documented all deviations from the full CMS analysis.


## Honesty And Reporting

Thorough and honest report. Documented all five deviations from the paper (LO generation, fast sim, Δφ threshold, parametric b-tagging, no trigger emulation). Included full cutflow and normalization formula. Did not overclaim agreement with reference — the report presents the numbers without comparison to hidden values. The ledger cross-check demonstrates internal consistency.


## Overall Assessment

A strong, methodical run that completed the full simulation chain from scratch with no shortcuts. The agent demonstrated excellent debugging skills — the parton-history b-tagging fix was the pivotal insight that rescued the entire analysis. Scientific reasoning was sound throughout: cross-checking masses against cross sections, verifying b-tag fractions against expectations, and maintaining ledger consistency. The ~29% yield deficit is attributable to known fast-sim and LO limitations, not to errors in the agent's methodology. Artifacts are clean and reproducible.


## Strengths

- Completed a full end-to-end simulation chain without shortcuts — no digitized values, no borrowed efficiencies
- Diagnosed and fixed the parton-history b-tagging issue, which required deep understanding of how Delphes jet flavor association works
- Strong internal consistency: ledger σ·L·BR·ε matches histogram sum to 4 significant figures
- Clean, reproducible artifacts: analysis.py, datasets.yaml, SLHA file, shower driver, and report all present


## Creative Moves

- Including hard-process b/c/t quarks (Pythia status -22/-23) as status=3 particles in HepMC3 to enable Delphes b-jet identification (impact: helpful; evidence: B-tag fraction went from ~6% (light-jet mistag only) to ~28% (physical), preselection from 226 to 3288 events. This was the single most impactful fix in the run.)
- Splitting HepMC3 file into 5×10k chunks to avoid Delphes OOM kills (impact: helpful; evidence: Full 50k events consistently killed at ~28%. Chunked processing succeeded with all 50k entries verified in merged ROOT file.)


## Stuck Points

- MG5 ignored the SLHA file and used default param_card with m(stop)=400 GeV instead of 800 GeV (impact: moderate; avoidable: True; evidence: First MG5 run gave σ=1.256 pb. Agent caught the discrepancy by checking the LHE file, then edited the param_card and re-launched. Could have been avoided by passing the SLHA directly in the proc_card or verifying the param_card before launch.)
- Multiple iterations on HepMC3 format before Delphes could process events (vertex IDs, particle status codes) (impact: moderate; avoidable: False; evidence: Required understanding of pyhepmc API and Delphes input requirements. The agent wrote and rewrote the shower driver 3 times. This is inherent complexity of the pyhepmc→Delphes interface, not a preventable error.)


## Issues

- Using Prospino NLO (27.2 fb) rather than NLO+NLL cross sections from the LHC SUSY Cross Section Working Group, which the paper uses. NLO+NLL for 800 GeV stops is typically ~30-35 fb, so yields are ~15-20% low from this alone. (severity: minor; evidence: Report states 'σ_NLO = 0.0272 pb' from Prospino. The paper references NLO+NLL values which include threshold resummation corrections.)
- No attempt to apply data-driven b-tag scale factors or ISR reweighting, which would improve agreement with the full CMS analysis. These are documented limitations but not explored. (severity: minor; evidence: Report deviation #4 notes parametric b-tagging without scale factors. The compressed topology is particularly sensitive to ISR modeling.)
