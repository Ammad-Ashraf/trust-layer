# Study A: public sources for the hand ledgers (collected 2026-11-26)

Collected ahead of M5 so the T5Wg and T2tt hand ledgers, and the 1d "neighbouring mass point" injections, use real published numbers. Everything here is public (LHC SUSY Cross Section WG twiki, CMS public results pages). Nothing comes from Collider-Bench's hidden answers.

## Cross sections, LHC SUSY Cross Section WG, 13 TeV

**Gluino pair (`SUSYCrossSections13TeVgluglu`, r10, 2024-12-09)**
- The current page only has **NNLOapprox+NNLL** (PDF4LHC21_40_pdfas, squarks decoupled). Uncertainty in %, symmetrized.
- 1700 GeV: 5.662E-03 pb ± 17.93%
- 1750 GeV: 4.342E-03 pb ± 19.05%
- 1800 GeV: 3.349E-03 pb ± 20.52%
- ⚠ CMS-SUS-16-046 (2017) normalized at **NLO+NLL**, which is no longer on the page. An NLO+NLL vs NNLOapprox comparison PDF (`compare_gg.pdf`) is attached there, not fetched. **Open:** which order the hand ledger uses. Lean: the paper's order (NLO+NLL), from an archived twiki revision. Fall back to NNLOapprox+NNLL with a note.
- For comparison, the smoke-run agent's Prospino NLO at 1750 GeV is 3.96 fb (LO 1.64 fb, K = 2.41), and MadGraph LO is 1.453 fb (transcript #24, #69).

**Stop pair (`SUSYCrossSections13TeVstopsbottom`, r14, 2024-12-09)**
- Again only **NNLOapprox+NNLL** (PDF4LHC21, decoupled). Same open question as above (CMS-SUS-16-051 used NLO+NLL).
- 750: 5.330E-02 pb ± 6.90% · 800: 3.482E-02 pb ± 7.26% · 850: 2.314E-02 pb ± 7.64% · 950: 1.068E-02 pb ± 8.55% · 1000: 7.395E-03 pb ± 9.08%

**Wino chargino–neutralino (`SUSYCrossSections13TeVn2x1wino`, r11, 2017-06-15)**
- NLO-NLL Resummino, envelope of CTEQ6.6 and MSTW2008nlo90cl. C1+N2 and C1−N2 summed; absolute uncertainties in fb.
- 500 GeV: 46.3533 ± 4.16461 fb · **550 GeV: 30.1656 ± 2.88065 fb** (matches the M2 ledger) · 600 GeV: 20.1372 ± 2.04438 fb
- Injection 1d-mass-500 uses **46.3533 fb** (the test case's 46.4 fb was an estimate; update it to this value in M5).

## CMS public cut flows (efficiency sources)

- **CMS-SUS-16-046, Additional Table 2:** cut flow of **T5Wg, m(gluino) = 1750, m(NLSP) = 1700 GeV**, at 35.9 fb⁻¹. This is our exact benchmark. It's an image only: `http://cms-results.web.cern.ch/cms-results/public-results/publications/SUS-16-046/CMS-SUS-16-046_Table-aux_002.png` (also `.pdf`). Additional Table 1 is the TChiWg 700 cut flow. No HEPData link on the page; INSPIRE 1637580.
- **CMS-SUS-16-051, Additional Tables 1–3:** signal cut flows (Table 1: stop → t χ̃⁰). Images only; their captions don't name the mass points, so open the files to see whether 800/400 or 1000/50 is included: `…/SUS-16-051/CMS-SUS-16-051_Table-aux_001.png` (and `_002`, `_003`). HEPData: `https://www.hepdata.net/record/ins1605128`.
- **M5 next step:** read these table images (PDF versions) for the event counts. HEPData blocks scripts, so open them by hand or read the PDF, as in M2.
