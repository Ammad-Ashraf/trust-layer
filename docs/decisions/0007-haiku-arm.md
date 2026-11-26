# 0007 — Add a Haiku 4.5 arm

- **Status:** decided
- **Date:** 2026-11-13
- **Decide by:** with 0005, after the smoke run

## Question

Add 18 Haiku 4.5 runs (about $1.09 each, roughly $20) as a guaranteed-signal arm?

## Claude's lean

Yes, together with picking tasks where the main model actually failed normalization. Errors are frequent with Haiku, and "the checker matters most where agents are weakest" is a finding on its own.

## Decision (Ammad)

Yes, decided 2026-11-27, alongside Sonnet 4.6 (0005). Why: Haiku makes frequent mistakes (R2 fabricated its whole ledger), so this arm is close to a guaranteed signal and cheap (about $20 at API prices).
