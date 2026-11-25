# Roadmap — Phase 1

Status: ⬜ not started · 🟨 in progress · ✅ done · ⏸ blocked. Update this file at the end of each session.

## Milestones

| # | Milestone | Dates | Done when | Status |
| --- | --- | --- | --- | --- |
| M1 | Set up repo and container | 11–17 Nov | One Collider-Bench task runs end to end on the runner; lab log started | ✅ 18 Nov |
| M2 | Learn the formula by hand | 16–29 Nov | `tasks/sus-16-034_sim-TChiWZ/ledger.yaml` filled by Ammad, with every unit and source, explainable in simple words | ✅ 24 Nov |
| M3 | Baseline run, label errors | 23 Nov–6 Dec | One baseline transcript read in full; every mistake labelled with a sub-gap code | ✅ 26 Nov |
| M4 | Build checker v0 | 30 Nov–15 Dec | C1–C5 pass unit tests; the gate blocks a bad ledger in a real test run | ✅ 26 Nov: gate sent a real agent back (R1 ok 6) and ran in a real harness run (R2). R2 also showed the checker passing a fabricated ledger → decision 0017 |
| M5 | Study A: error injection | 9–22 Dec | Catch rate per sub-gap and false-alarm rate, for 3 tasks | ⬜ |
| M6 | Study B: 18 agent runs | 16 Dec–5 Jan | 18 scored runs, with and without the checker, each labelled | ⬜ |
| M7 | Note + public repo | 4–15 Jan | 2–4 page note, public repo, one results table quotable in the motivation letter | ⬜ |
| — | CERN openlab deadline | **21 Jan 2027** | Application submitted | ⬜ |
| — | Send results to Collider-Bench authors | 25 Jan 2027 | Email sent; includes every entry in [collider-bench-findings.md](outreach/collider-bench-findings.md) | ⬜ |

## Features (checker v0)

| Feature | Path | Guards | Status |
| --- | --- | --- | --- |
| Ledger + `record-quantity` CLI | `src/trustlayer/ledger/` | all of 1a–1e (records inputs) | ✅ 26 Nov |
| C1 Units | `src/trustlayer/checks/` | 1a | ✅ 26 Nov |
| C2 Source | `src/trustlayer/checks/` | 1b | ✅ 26 Nov |
| C3 Complete formula | `src/trustlayer/checks/` | 1c | ✅ 26 Nov |
| C4 Match | `src/trustlayer/checks/` | 1d | ✅ 26 Nov |
| C5 Carried through | `src/trustlayer/checks/` | 1e | ✅ 26 Nov |
| Gate (Stop hook, bounce cap 3, bounce log) | `src/trustlayer/gate/` | — | ✅ 26 Nov (tested in the container and a real run) |
| Injector for Study A | `src/trustlayer/inject/` | — | ⬜ |
| Report (results tables) | `src/trustlayer/report/` | — | ⬜ |
| Container integration (mount CLI + hook) | `integration/` | — | ✅ 26 Nov: `simple_ledger` + `scripts/run-checker-arm` work on the runner; fork still pending (before Study B) |

## This week (13–17 Nov)

- [x] Scaffold the repo and push it to GitHub (private)
- [x] Connect to the runner laptop (Claude Code on the runner, driven remotely)
- [x] Clone the repo with submodules on the runner; pull the Collider-Bench container; record the image digest
- [ ] Create a separate, spend-limited Anthropic API key for benchmark runs only (smoke run used OAuth; see 0011)
- [x] Smoke run → `experiments/00-smoke-run/` (T5Wg, Sonnet 4.6, OAuth; δ_norm 0.98, failed on ε)
- [x] Map the four attachment points → `integration/attachment-points.md`
- [ ] Send the two compute emails (supervisor, NCP) — bonus track
- [x] Read the paper's per-task tables; note where each model failed normalization (→ 0014: T2tt_SRG shows no counting gap; lean swap to T2tt_comp)

## Next (from 18 Nov)

- [x] Decide 0008–0013 (Claude, delegated by Ammad on 18 Nov)
- [ ] Ammad: ask Israr for OK to add a `tlsubject` user on his laptop (0010)
- [x] Runner: commit the smoke run's `session.jsonl.gz`, `analysis.py` and `report.md` (0012); check the photon–jet guess (ruled out; the real cause is the gravitino, see M3)
- [x] M3: smoke-run transcript read in full and labelled → `labels.yaml` + `results/m3-review.md` (0 Gap-1 errors; 3a, 3b, 3c, 3d + 1 uncoded)
- [x] Windows: build the `simple_ledger` agent folder (0008) → M4 step 6 (26 Nov). Still open: put it in a Collider-Bench fork and repin the submodule, before Study B

## This week (30 Nov–6 Dec): M4 checker v0, steps from [checker-v0.md](design/checker-v0.md) §8

- [x] Ammad: decide 0016 → A: Study A's injections and τ = 5% fixed before the checks (26 Nov)
- [x] Step 2: `ledger` schema v2 + unit table + load/save (reads the v1 hand ledgers) (26 Nov)
- [x] Step 3: `record-quantity` CLI incl. `show` (26 Nov; 73 tests, ruff and mypy clean)
- [x] Step 4: C1–C5 + registry, tests first; sus-16-034 hand ledger upgraded to v2; task contexts for 5 tasks (26 Nov)
- [x] Step 5: gate (Stop hook, bounce cap 3, bounce log) (26 Nov)
- [x] Step 6: agent-folder build script, shims, fairness test on the built folder, post-run tamper check (26 Nov)
- [x] Step 7 (runner): task R1 in [runner-tasks.md](runner-tasks.md) (container test + `--claude-hook`)
- [x] Step 8 (runner): task R2 in [runner-tasks.md](runner-tasks.md) (one cheap `simple_ledger` run) → **M4 done**
- [ ] Before Study B: Collider-Bench fork with the agent folder, submodule repinned (0008; creating a public fork needs Ammad's OK)
- [x] Update `docs/engineering-standards.md`: no `pint` inside the container (0009); `pint` is now a dev dependency
- [x] M2 prep: confirm task id (`sus-16-034_sim-TChiWZ`), find public sources, write the fill guide; rename `tasks/` folders to full task ids
- [x] M2: fill `tasks/sus-16-034_sim-TChiWZ/ledger.yaml` by hand, step by step (5.41 events, matches CMS's cut flow); revision story in `story.md`

## Parking lot (not Phase 1)

Second-opinion recalculation · ε-plausibility check (3c; the M3 read shows it would have caught the smoke run: reco vs truth missing momentum) · provenance check (leading Phase 2 candidate) · human escalation · HEPTABench as a second test bed.
