# 0005 — Which model Study B tests

- **Status:** decided
- **Date:** 2026-11-13
- **Decide by:** after the smoke run, before the baseline weeks (about 1 Dec)

## Options

| Option | Good | Bad |
| --- | --- | --- |
| Sonnet 4.6 | Paper baseline exists; about $137 for 18 runs; fits the $300 cap | Weaker headline |
| Opus 4.7 | Paper baseline exists; strongest headline ("helps even the strongest model") | About $255; may make too few errors to show an effect (power risk) |
| Newest model | Interesting | No paper numbers to compare against |

## Claude's lean

Decide with real per-task cost and runtime from the smoke run. The "paper used it" argument applies to both Opus 4.7 and Sonnet 4.6.

## Notes

On 11 Nov Ammad leaned Opus 4.7 for Study B and a newer model where no paper comparison is needed. Ammad also asked whether the Claude Pro subscription could replace API credits; a Pro run can stop at the 5-hour usage limit mid-task, which would ruin that data point.

## Decision (Ammad)

Sonnet 4.6, decided 2026-11-27. Why: the paper has Sonnet 4.6 numbers, so our no-checker arm can be sanity-checked against them; the paper's tables show Sonnet often gets the counting wrong on all 3 target tasks (total vs shape error 0.30/0.07, 0.61/0.15, 0.69/0.26), so there is room for the checker to help; and it costs about half of Opus 4.7. The baseline is our own no-checker arm (same model, machine and versions); the paper is only the sanity check. With Sonnet chosen, 0014's task swap stands: Study B uses `T2tt_comp`, not `T2tt_SRG`.
