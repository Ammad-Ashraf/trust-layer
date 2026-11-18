# 0012 — Commit run transcripts?

- **Status:** open
- **Date:** 2026-11-18
- **Decide by:** before M3

## Question

Decision 0004 deferred this until the size was known. A transcript is 1.2 MB (107 turns). What do we commit per run?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Commit `session.jsonl.gz`, `analysis.py` and `report.md` per run | Labels are reproducible from the repo; the M3 read can happen on the Windows laptop | About 0.3 MB per run gzipped; transcripts become public with the repo |
| B. Keep transcripts on the runner only | Repo stays small | Labels can't be checked without the runner; risk of losing them |

Never committed in either case: `workspace/sims`, `workspace/data` (1.35 GB) and `.claude_home/` (credentials).

## Claude's lean

A. The labels are the result; the transcript is their evidence.

## Decision (Ammad)

—
