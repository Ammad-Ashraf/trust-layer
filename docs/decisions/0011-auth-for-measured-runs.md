# 0011 — Auth for measured runs

- **Status:** open
- **Date:** 2026-11-18
- **Decide by:** with 0005 and 0006

## Question

Should measured runs (baseline, Study B) use the subscription login (OAuth) or a spend-limited API key?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. API key with a spend limit | Headless and reliable; parallel runs fine; cost is exact | Real money ($5.68 per Sonnet 4.6 run at max effort in the smoke run) |
| B. OAuth (subscription) | Smoke run cost nothing extra | Refresh-token race on runs longer than the token life; 5-hour usage limits; logs Ammad's account into the runner |
| C. OAuth for one-off runs, API key for Study B | Cheap while developing | Two setups to maintain |

## Claude's lean

C. OAuth is fine for single development runs started right after a fresh login. Study B's long and parallel runs need an API key.

## Decision (Ammad)

—
