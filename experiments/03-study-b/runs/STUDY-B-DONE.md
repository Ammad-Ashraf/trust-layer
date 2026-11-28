# Study B: done (28 Nov 2026)

1. **What ran:** 36 slots, all `scored`, with 0 timeouts and 0 crashes. Setup frozen at `study-b-v1` throughout. Two void attempts, both S05 and both infrastructure (a gate cwd bug, then a laptop move), rerun. About 19 h of wall-clock including voids, $0. Details: [`R7-report.md`](R7-report.md); numbers: [`../results/study-b.md`](../results/study-b.md).
2. **Sonnet 4.6, without vs with the checker:** 4/9 vs 3/9 pass (norm L2 < 0.33), median Δ_norm 0.34 vs 0.34, Gap-1 errors 7 in 6/9 runs vs 7 in 5/9. **No measurable effect.**
3. **Haiku 4.5, without vs with the checker:** 0/9 vs 0/9 pass, median Δ_norm 8.77 vs 0.98. Gap-1 errors 16 in 9/9 vs 26 in 9/9 runs. Judge FAILED 7/9 vs 4/9. Fewer wild totals and fewer judge FAILs with the checker, but no passes, and more labelled Gap-1 errors.
4. **The checker gets gamed:** 7 of 7 bounced Haiku runs gamed at least one bounce, and 2 of 4 bounced Sonnet runs did. The ways seen: relabelling σ's source (6 runs: `xsec_wg`, `paper`, `other`), inventing `n_pass`/`n_gen`, and back-solving ε or rescaling bins to meet C5. Two runs hit the bounce cap and passed with warnings (S22, S25).
5. **What the checker can't see:**
   - a σ that covers one charge channel only (S17, S25), because the ledger can't hold a sum (and C2 rejected a correct sum in S06);
   - events at the wrong mass point (8 runs, almost all Haiku);
   - simulation faults such as the gravitino left visible in the stock Delphes card or no extra jets matched in.
   Most large misses came from these, not from bookkeeping. 18 findings with fix ideas: [`CHECKER-NOTES.md`](CHECKER-NOTES.md).
6. **Timeouts and voids per arm:** 0 timeouts anywhere. Voids: Sonnet checker 2 (S05), all other arms 0.
7. **Early stops (labels):** Haiku baseline 7, Haiku checker 0, Sonnet 1 per arm. The gate's bounces keep Haiku working instead of quitting, so early stopping is a confound for the arm comparison, as flagged in R6.
8. **Benchmark problems found (for the Collider-Bench authors):**
   - `read-paper` and `prospino --slha` reject relative paths (F7);
   - the stock Delphes card doesn't make the gravitino invisible (F8);
   - details in `docs/outreach/collider-bench-findings.md`.
9. **Odd:** the judge sometimes repeats an agent's false claim (S26) or "corrects" a fabricated count (S32). `n_gen` is null in every manifest (code fix after Study B).
