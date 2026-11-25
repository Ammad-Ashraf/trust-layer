# M3 review: the smoke-run transcript, read in full (2026-11-26)

Milestone M3 asks for one baseline transcript read in full, with every mistake given a sub-gap code. This is that read for the 18 Nov smoke run (T5Wg, Sonnet 4.6, no checker). The labels themselves are in [`labels.yaml`](../runs/20261118-0109_sus-16-046_baseline_1/labels.yaml). This page says what they mean.

**What was read:** all 145 steps of `session.jsonl.gz`, plus `analysis.py`, `report.md`, the score and the paper's selection (Sec. 4–5, Table 1). The transcript was turned into readable text with a throwaway script; the step numbers (#N) in the labels follow that order.

## The one-line answer

**The counting was right; the simulated detector was wrong.** Every number our checker looks at was correct. The agent lost 99 of every 100 events in the simulation and the cuts, and never noticed.

## The fishing picture again

Expected events = σ × L × BR × ε. In the analogy: how common the fish is × how much water you sweep × the share that are the right kind × how many your net keeps.

| Factor | Agent's value | Right? |
| --- | --- | --- |
| σ (how common) | 3.96 fb, from Prospino, pb → fb done properly | ✅ |
| L (water swept) | 35.9 fb⁻¹ | ✅ |
| BR (right kind) | 50/50 gluino decays, as the paper says | ✅ |
| ε (net keeps) | 0.93% | ❌ about 39% was needed |

## Where the events went (the agent's own counts, out of 10,000)

| Step | Events left | Lost here |
| --- | --- | --- |
| A hard photon in the central detector | 4,329 | |
| + missing momentum > 300 GeV | 247 | **94%** |
| + the other photon and S_T cuts | 201 | small |
| + the two jet rules | 93 | about half |

On 18 Nov I guessed the photon–jet rule was the main hole. The full transcript shows it isn't: **the big loss is the missing-momentum cut**, and the jet rules only add a factor of about 2. The detector card also rules out the 18 Nov guess itself: it already removes the jet built from the photon.

## The five mistakes, in plain words

1. **L1 · 3a, the invisible particle was made visible.** The signal ends in two gravitinos that escape the detector, like two fish slipping out of the net unseen. Their escape is what "missing momentum" measures. The standard detector settings list neutrinos and neutralinos as invisible but not the gravitino, so the simulated calorimeter "caught" it as a jet. It's like a scale that counts the fish that got away as part of the catch. **Confirmed on the runner (26 Nov):** with the gravitinos treated as invisible, 72% of events have missing momentum above 300 GeV; in the simulated detector only 9% do, and in 2,972 of 3,000 events a jet sits right on a gravitino.
2. **L2 · 3c, no sanity check.** The agent saw that only 9% of events had large missing momentum, wrote "Good.", and later accepted 0.93% as the final efficiency. Both numbers should have stopped it. The truth gravitinos and the detector's own truth-level missing momentum were in the same file, one line away.
3. **L3 · 3d, wrong diagnosis.** The report blames a "missing lepton veto". The paper says plainly that there is no lepton veto, and a veto would only make the yield *smaller*, when it was already 50× too small. Anyone reading the report would look in the wrong place.
4. **L4 · 3b, jet rules applied to every jet.** The paper first keeps only jets above 30 GeV that aren't sitting on a photon or lepton, then applies the two jet rules. The agent applied them to every jet, including the fake ones from L1. This costs about a factor of 2.
5. **L5 · no code, a fix lost when the context was cut.** The agent wrote "let me fix this" for L4, its context was then compacted, and after that the fix was never made; the report lists it as a known deviation instead. None of our codes fits a slip like this, so it is recorded without one.

**Count:** 0 Gap-1 errors (1a–1e), 0 fabrication (2a–2e), 4 judgment errors (3a, 3b, 3c, 3d), 1 uncoded.

## What this means for the project

- **Our checker would have passed this run.** C1–C5 check the counting, and the counting was right. This is the honest result, and the note will say so.
- **It doesn't overturn the plan.** One run on one task is a hint. The paper's tables over hundreds of runs show shapes mostly right and totals wrong (Gap 1, decision 0014). In this run the shape was wrong too, so it's the unusual kind of failure.
- **It strengthens one parking-lot idea.** A cheap plausibility check on ε (for example "is reco missing momentum anywhere near the truth?") would have caught this run. That is outside Phase 1's scope guard and stays parked. It is now the best-supported Phase 2 candidate after provenance.
- **Two design inputs for M4:**
  - The gate runs once, at the end. L5 shows that an agent can decide on a fix and then lose it when its context is cut, so checking only the end state is the right design.
  - The ledger must record where ε came from (passing events ÷ generated events, plus the script that produced them). Then C5 can tie the submitted bins back to the ledger instead of trusting a single number.

## Not done, or still open

- **σ order.** The paper uses NLO+NLL cross sections; the agent used Prospino NLO. Our C2 rule allows that. The size of the difference at 1750 GeV goes into the T5Wg hand ledger during Study A.
