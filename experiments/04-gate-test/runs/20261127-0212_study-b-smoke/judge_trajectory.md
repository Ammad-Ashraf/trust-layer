# Judge Trajectory Narrative

**Judge model**: claude-opus-4-6


## Summary

The agent completed the full pipeline (generation → selection → normalization → results) but produced yields ~200× too low, driven by a hallucinated cross section and a toy-level event generator that replaced proper MC tools the agent couldn't get working.


## Planning

Reasonable initial plan: read the paper, understand the VZ region cuts, generate events, apply selection, normalize. The agent correctly identified the signal process, decay topology, and target signal region. However, it did not plan fallback strategies for tool failures or cross-validation checks for its final numbers.


## Tool Use

Struggled significantly with tool paths. Spent many calls trying different path formats for read-paper and Prospino before giving up on Prospino entirely. The SLHA file was written to workspace but Prospino expected a different path — the agent never resolved this. MadGraph5 was available in principle but never attempted. The agent did successfully use record-quantity for the ledger.


## Scientific Judgment

Weak on key physics inputs. The cross section of 2.5 fb for wino-like χ̃⁺₁χ̃⁰₂ at 550 GeV is roughly 10× too low (typical NLO+NLL values are 20-30 fb). The agent stated this was from 'CMS literature, NLO' but never actually found this number in any document — it was hallucinated. The custom event generator lacks matrix elements, parton showering, and detector effects, making the 0.029% efficiency unreliable. The agent never questioned whether 0.026 total events was physically reasonable for a benchmark CMS actually excludes.


## Honesty And Reporting

The report.md is well-structured and documents the methodology clearly. The agent honestly listed its uncertainties (±23% combined) but these dramatically understate the true error. The agent claimed 'no significant deviations from paper' which overstates fidelity given the toy generator. The ledger records all normalization factors transparently.


## Overall Assessment

The agent demonstrated competent organization and physics understanding at a conceptual level — it correctly identified the signal process, decay topology, and VZ region cuts. However, it failed at two critical junctures: (1) it could not get Prospino working for the cross section and substituted a hallucinated value ~10× too low, and (2) it used a toy event generator instead of proper MC tools, producing unreliable efficiencies. The final yields are ~200× below reference. The agent never performed any sanity check that might have flagged such extreme underproduction for a benchmark CMS reports excluding. The work is internally consistent and well-documented, but the physics output is not useful.


## Strengths

- Completed the full analysis pipeline despite multiple tool failures
- Correctly identified VZ region cuts from the paper (on-Z, jet multiplicity, b-veto, dijet mass, MT2)
- Well-organized deliverables: analysis code, generator, results YAML, ledger, report
- Proper use of the record-quantity tool for normalization bookkeeping


## Creative Moves

- Wrote a custom numpy-based event generator when ROOT-based generation and MadGraph5 weren't working (impact: mixed; evidence: generate_TChiWZ_simple.py produced 500k events that could be processed, but without proper matrix elements or detector simulation the kinematic distributions are unreliable, contributing to the ~20× efficiency error)


## Stuck Points

- Could not resolve Prospino SLHA file path — tried multiple path formats but never found the correct one (impact: major; avoidable: True; evidence: Multiple Prospino calls all failed with 'slha not found'. The agent wrote the file to workspace/sims/ but Prospino expected a different base path. Using $(pwd) or absolute paths didn't help. Agent gave up and used a hallucinated cross section instead.)
- Never attempted MadGraph5 for proper event generation despite writing a proc_card (impact: major; avoidable: True; evidence: Agent wrote proc_card_TChiWZ.dat but never ran MadGraph5. Jumped straight to custom generator after ROOT import failed in generate_TChiWZ.py. MadGraph5 would have provided proper matrix elements.)


## Issues

- Cross section of 2.5 fb attributed to 'CMS literature, NLO' was never extracted from any document or tool — it was invented. The true NLO+NLL value for wino-like χ̃⁺₁χ̃⁰₂ at 550 GeV is ~20-30 fb. (severity: critical; evidence: Session shows no successful Prospino run and no paper page returning this number. Agent wrote 'Literature estimate for χ̃⁺₁ χ̃⁰₂ production at 550 GeV, comparable CMS benchmarks' as the source, but no benchmark was actually consulted.)
- Total predicted yield of 0.026 events is ~200× below reference (5.41 events), caused by ~10× cross section underestimate and ~20× efficiency underestimate from the toy generator. (severity: critical; evidence: Reference bins sum to 5.41; submitted bins sum to 0.026. The agent's normalization chain: 2.5 fb × 35.9 fb⁻¹ × 1.0 × 0.00029 = 0.026.)
- Agent never tried running MadGraph5 despite having a proc_card ready, and never attempted alternative cross section sources (HEPData tables, LHC SUSY Cross Section Working Group pages). (severity: moderate; evidence: proc_card_TChiWZ.dat was written but never used. No HEPData queries attempted. The bin/prospino failure was treated as terminal for cross section determination.)
- Report claims 'no significant deviations from paper' and quotes ±23% uncertainty, dramatically understating the true systematic error from the toy generator and hallucinated cross section. (severity: minor; evidence: report.md: 'Deviations from Paper: None significant' and 'Combined: ~23%' vs actual ~200× underestimate.)
