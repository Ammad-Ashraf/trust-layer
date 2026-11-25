# Findings to report to the Collider-Bench authors

A running list of benchmark-level problems we hit while using Collider-Bench. **Read this before any contact with the authors:** the 25 Jan 2027 results email, a cold email, an issue, or a pull request to their repo. Each entry carries its evidence, so we can state it with a number or a source.

Rules for this file:
- Add an entry the day we find it.
- Never put answer-key values here (hidden reference yields, our `tasks/` ledgers). Agent-visible facts only.
- When an entry has been reported, fill in **Reported** (date, channel, link) instead of deleting it.

Pinned context for every entry, unless stated otherwise: Collider-Bench commit `2986d8b`, image `ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3…` (created 2026-05-03), Claude Code 2.1.326 on the runner laptop.

---

## F1 · The stock Delphes CMS card makes the gravitino visible (high impact)

- **Found:** 2026-11-26, M3 read of the smoke run (`experiments/00-smoke-run/`, labels L1–L2).
- **What:** `/opt/sim/delphes/cards/delphes_card_CMS.tcl` in the image lists neutrinos (12, 14, 16) and neutralinos (1000022, 1000023, 1000025, 1000035, 1000045) as invisible in its `EnergyFraction` lists, but **not the gravitino (1000039)**. The HCal default `{0} {1.0}` therefore deposits each gravitino's full energy, and it is reconstructed as a jet. `NeutrinoFilter` doesn't list 1000039 either, so `GenMissingET` is wrong too.
- **Why it matters:** the agents' own `AGENTS.md` cheat-sheet points them at this exact card (`DelphesHepMC3 "$DELPHES_DIR/cards/delphes_card_CMS.tcl" ...`). Every task whose signal ends in gravitinos inherits the trap, e.g. `sus-16-046_sim-T5Wg` and `sus-16-046_sim-TChiWg`. An agent that follows the cheat-sheet loses most of its missing momentum and fails, through no misreading of the paper.
- **Evidence (smoke run, T5Wg_1750_1700, Sonnet 4.6, first 3,000 events of the run's own ROOT file):**

  | Quantity | Mean | Fraction > 300 GeV |
  | --- | --- | --- |
  | Truth invisible MET (gravitinos + neutrinos) | 487.5 GeV | 72.4% |
  | Delphes `GenMissingET` | 82.4 GeV | 8.3% |
  | Delphes reco `MissingET` | 127.6 GeV | 9.2% |

  In 2,972 of 3,000 events, a jet with p_T > 100 GeV lies within ΔR < 0.4 of a truth gravitino. The run's signal-region efficiency came out at 0.93% and it failed (δ_norm 0.98).
- **Suggested fix:** add `add EnergyFraction {1000039} {0.0}` to both the ECal and HCal blocks, and `add PdgCode {1000039}` to `NeutrinoFilter`. Or ship a GMSB-ready card and name it in the cheat-sheet for gravitino tasks.
- **Open question for them:** how many of the paper's T5Wg/TChiWg failures share this cause? It may also explain part of the per-task spread they report (Sonnet 4.6 on T5Wg: 0.61 ± 0.46).
- **Reported:** not yet.

## F2 · The harness copies the host's Claude settings into the subject agent (medium, safety and fairness)

- **Found:** 2026-11-18, smoke run (`notes.md` point 4; `integration/attachment-points.md` §2).
- **What:** `agent_runtime/vendors.py:224-227` copies the host user's `~/.claude.json`, `~/.claude/.credentials.json` and `~/.claude/settings.json` into the fake `$HOME`. On our runner, that handed the subject agent an MCP server with auth headers and the account's claude.ai connectors (mail, drive, …), all under `--dangerously-skip-permissions`.
- **Why it matters:** results then depend on whatever the host user has installed, and the agent can reach personal accounts.
- **Suggested fix:** build the subject's settings from a fixed template, and set `ENABLE_CLAUDEAI_MCP_SERVERS=false` by default.
- **Reported:** not yet.

## F3 · Newer Claude Code versions give the subject agent extra tools (low–medium, comparability)

- **Found:** 2026-11-18, smoke run (`notes.md` point 6).
- **What:** the harness blocks only `ScheduleWakeup` (`vendors.py:217`). Claude Code 2.1.326 also offers `RemoteTrigger`, `CronCreate`, `PushNotification`, `SendMessage`, `Workflow` and built-in skills. The transcript's init event lists them.
- **Why it matters:** scores from newer CLI versions aren't directly comparable to the paper's, and some of these tools reach the user's account.
- **Suggested fix:** an allow-list of tools in `configs/claude.yaml`, recorded in `run_info.json`.
- **Reported:** not yet.

## F4 · Small documentation drifts (low)

- **Found:** 2026-11-18, smoke run.
- **What:**
  - The image has no `claude` baked in (`/opt/node-global/bin` is absent), despite `docker/README.md`; the harness bind-mounts the host binary.
  - The image is 3.9 GB to download and 8.5 GB unpacked; the docs say about 3.5 GB.
  - The repo's CLAUDE.md names transcripts `*.stream.jsonl`; they are written to `workspace/session.jsonl` (`launch.py:162`).
- **Reported:** not yet.

---

## What we'll also offer them

- Our checker and Study A suite as an optional add-on (the `simple-ledger` agent folder), with results.
- The M3 labelling method (sub-gap codes per mistake), as a way to read failures beyond δ_norm.
