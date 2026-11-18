# 0009 — `pint` inside the container

- **Status:** open
- **Date:** 2026-11-18
- **Decide by:** start of M4

## Question

The image's `lhc_analysis` env has `pyyaml` but not `pint`. How does the in-container ledger and gate handle units?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Drop `pint` for the in-container part; fixed unit table (pb, fb, fb⁻¹, dimensionless), standard library only | Nothing extra to mount; simple to audit | We maintain a small unit table; less general |
| B. Vendor `pint` into the read-only mount | Full unit algebra | More to mount and pin; version drift vs the image's Python 3.11 |

## Claude's lean

A. The normalization formula only needs a handful of units. `pint` can stay for host-side tools if needed.

## Decision (Ammad)

—
