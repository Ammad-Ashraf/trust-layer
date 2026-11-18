# Roadmap — Phase 1

Status: ⬜ not started · 🟨 in progress · ✅ done · ⏸ blocked. Update this file at the end of each session.

## Milestones

| # | Milestone | Dates | Done when | Status |
| --- | --- | --- | --- | --- |
| M1 | Set up repo and container | 11–17 Nov | One Collider-Bench task runs end to end on the runner; lab log started | ✅ 18 Nov |
| M2 | Learn the formula by hand | 16–29 Nov | `tasks/sus-16-034/ledger.yaml` filled by Ammad, with every unit and source, explainable in simple words | ⬜ |
| M3 | Baseline run, label errors | 23 Nov–6 Dec | One baseline transcript read in full; every mistake labelled with a sub-gap code | ⬜ |
| M4 | Build checker v0 | 30 Nov–15 Dec | C1–C5 pass unit tests; the gate blocks a bad ledger in a real test run | ⬜ |
| M5 | Study A: error injection | 9–22 Dec | Catch rate per sub-gap and false-alarm rate, for 3 tasks | ⬜ |
| M6 | Study B: 18 agent runs | 16 Dec–5 Jan | 18 scored runs, with and without the checker, each labelled | ⬜ |
| M7 | Note + public repo | 4–15 Jan | 2–4 page note, public repo, one results table quotable in the motivation letter | ⬜ |
| — | CERN openlab deadline | **21 Jan 2027** | Application submitted | ⬜ |
| — | Send results to Collider-Bench authors | 25 Jan 2027 | Email sent | ⬜ |

## Features (checker v0)

| Feature | Path | Guards | Status |
| --- | --- | --- | --- |
| Ledger + `record-quantity` CLI | `src/trustlayer/ledger/` | all of 1a–1e (records inputs) | ⬜ |
| C1 Units | `src/trustlayer/checks/` | 1a | ⬜ |
| C2 Source | `src/trustlayer/checks/` | 1b | ⬜ |
| C3 Complete formula | `src/trustlayer/checks/` | 1c | ⬜ |
| C4 Match | `src/trustlayer/checks/` | 1d | ⬜ |
| C5 Carried through | `src/trustlayer/checks/` | 1e | ⬜ |
| Gate (Stop hook, bounce cap 3, bounce log) | `src/trustlayer/gate/` | — | ⬜ |
| Injector for Study A | `src/trustlayer/inject/` | — | ⬜ |
| Report (results tables) | `src/trustlayer/report/` | — | ⬜ |
| Container integration (mount CLI + hook) | `integration/` | — | 🟨 map done; design in 0008–0010 |

## This week (13–17 Nov)

- [x] Scaffold the repo and push it to GitHub (private)
- [x] Connect to the runner laptop (Claude Code on the runner, driven remotely)
- [x] Clone the repo with submodules on the runner; pull the Collider-Bench container; record the image digest
- [ ] Create a separate, spend-limited Anthropic API key for benchmark runs only (smoke run used OAuth; see 0011)
- [x] Smoke run → `experiments/00-smoke-run/` (T5Wg, Sonnet 4.6, OAuth; δ_norm 0.98, failed on ε)
- [x] Map the four attachment points → `integration/attachment-points.md`
- [ ] Send the two compute emails (supervisor, NCP) — bonus track
- [ ] Read the paper's per-task tables; note where each model failed normalization

## Next (from 18 Nov)

- [x] Decide 0008–0013 (Claude, delegated by Ammad on 18 Nov)
- [ ] Ammad: ask Israr for OK to add a `tlsubject` user on his laptop (0010)
- [ ] Runner: commit the smoke run's `session.jsonl.gz`, `analysis.py` and `report.md` (0012); check the photon–jet guess
- [ ] Runner: 3 baseline runs on 3 tasks, on the subscription (0013) → labels
- [ ] Windows: fork Collider-Bench and add the `simple-ledger` agent folder (0008)
- [ ] M2: fill `tasks/sus-16-034/ledger.yaml` by hand

## Parking lot (not Phase 1)

Second-opinion recalculation · ε-plausibility check (3c; from the smoke run) · provenance check (leading Phase 2 candidate) · human escalation · HEPTABench as a second test bed.
