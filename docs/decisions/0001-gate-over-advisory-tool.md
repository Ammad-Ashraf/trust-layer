# 0001 — The checker reaches the agent as a gate

- **Status:** decided
- **Date:** 2026-11-11

## Question

How does the checker reach the test-subject agent?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| Advisory tool the agent may call | Less intrusive | The agent may ignore it, so we can't tell what helped |
| Gate: runs every time the agent tries to finish and sends errors back | Same treatment in every run | Uses wall-clock time inside the 2.5 h budget |

## Claude's lean

Gate, so the treatment is identical across runs.

## Decision (Ammad)

Gate: it's safer, and the agent hits it every time without being told to.

**Guards added 13 Nov:** at most 3 bounces, then submit with warnings · log every bounce · report wall-clock and tokens per arm · record N_gen per run.
