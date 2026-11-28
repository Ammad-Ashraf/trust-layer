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
- **A workaround that worked:** S26 (Sonnet, T5Wg, baseline) dropped `|pid| == 1000039` from the HepMC before Delphes (transcript line 402) and got ε 0.50 against 0.425 and δ_norm 0.08. S28 (Sonnet, T5Wg, checker) saw median MET of 93 GeV, found the gap in the card, and added `EnergyFraction {1000039} {0.0}` itself (transcript lines 1140–1155). It got δ_norm 0.005. So the task can be done, but only by an agent that thinks of it (S26 and S28 did; S16 and S18 didn't; the earlier Sonnet T5Wg runs S02 and S05 aren't checked for this yet).
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

## F5 · Agent names are hard-coded, so add-on agents need a side door (low, extensibility)

- **Found:** 2026-11-26, M4 runner task R2.
- **What:** `agent_runtime/config.py:43` (`_ALLOWED_AGENTS = {"simple"}`) and the dispatch `case` in `scripts/run-agent` accept only built-in agent names. A new folder under `agents/` can't be launched through the sanctioned entry point without editing the benchmark. We launch ours with `scripts/run-checker-arm`, which reuses their `run_with_compute` and `launch_single_run` unchanged.
- **Also:** `run-agent` fails with `activate_lhc_analysis: no harness-ready Python` unless `.venv` is activated first. CLAUDE.md shows the activation only in the one-time setup block.
- **Suggested fix:** discover agents from `agents/*/run.py`, or allow an `agent_module:` config key.
- **Reported:** not yet.

## F6 · The Pythia xmldoc in `$PYTHIA8_DIR` doesn't match the Python module (low–medium)

- **Found:** 2026-11-26, in both the smoke run (#78) and our R2 run (#67, #73).
- **What:** `pythia8.Pythia("$PYTHIA8_DIR/share/Pythia8/xmldoc")` aborts with "unmatched version numbers: in code 8.312 but in XML 8.313". The conda env's xmldoc (`$CONDA_PREFIX/share/Pythia8/xmldoc`) works. `SIMULATE.md` points agents at `$PYTHIA8_DIR`.
- **Why it matters:** Sonnet worked around it, but Haiku didn't. It fed undecayed LHE straight to Delphes, got no leptons, and then fabricated the answer. The environment pushes weaker agents toward failure for reasons that have nothing to do with physics.
- **Suggested fix:** ship a matching xmldoc, or point the docs and the `simulate` tool at the conda copy.
- **Reported:** not yet.

## F7 · `bin/read-paper` rejects relative paths from the workspace (medium, pushes weaker agents off the paper)

- **Found:** 2026-11-28, Study B S08 (Haiku 4.5, T5Wg). The same error appears in S05 (Sonnet, T5Wg) and S07 (Haiku, T2tt).
- **What:** `ColliderBench/bin/read-paper` runs `cd "${REPO_ROOT}"` before `python -m ColliderBench.tools.CLI.read_paper "$@"`. The natural call from the workspace, `bin/read-paper papers/CMS-SUS-16-046.pdf`, then fails with `ERROR: file not found: papers/CMS-SUS-16-046.pdf`, even though `ls papers/` shows the file. Only an absolute path works.
- **Why it matters:** S08 retried five times (transcript lines 32–48), gave up on the paper and went to WebFetch, then fabricated its efficiency and bins. Sonnet worked around it. Like F6, this is an environment failure that has nothing to do with physics, and it hits weaker agents harder. It affects both Study B arms the same way.
- **Also:** `bin/prospino --slha <relative path>` fails the same way (S24, transcript line 95), and S21 hit the `read-paper` case too.
- **Suggested fix:** resolve the path argument against the caller's working directory before the `cd` (e.g. `realpath` the first argument), or don't `cd` at all.
- **Reported:** not yet.

---

## F8 · The stock Delphes CMS card doesn't treat the gravitino as invisible (medium, silently breaks GMSB tasks)

- **Found:** 2026-11-28, Study B S16 (Sonnet 4.6, T5Wg, baseline). Seen again in S18 (Sonnet 4.6, T5Wg, checker): ε 0.037 against 0.425. That agent set `1000039:isVisible = off` in Pythia (transcript line 352), but Delphes ignores that flag, and it copied the stock card unchanged (line 790).
- **What:** the container's `/opt/sim/delphes/cards/delphes_card_CMS.tcl` sets `EnergyFraction 0` in ECal and HCal for the neutralinos (1000022, 1000023, 1000025, 1000035) and 1000045, but not for the gravitino (1000039). In T5Wg the LSP is the gravitino, so with the stock card its energy lands in the calorimeter and the missing energy mostly disappears. S16 got ε 0.045 against the reference 0.425 (only 963 of 8254 preselected events passed the MET/MT cuts) and never noticed why.
- **Why it matters:** the T5Wg task (SUS-16-046) can't be done right with the default card unless the agent knows to patch it. An agent that does physics sensibly but trusts the provided card fails by about 10×. This is an environment trap, not a normalization error, and it affects both Study B arms the same way.
- **Suggested fix:** add `add EnergyFraction {1000039} {0.0}` next to the neutralino lines in both calorimeter modules (it is in newer upstream Delphes cards), or mention in the T5Wg task that the gravitino must be made invisible.
- **Reported:** not yet.

---

## What we'll also offer them

- Our checker and Study A suite as an optional add-on (the `simple-ledger` agent folder), with results.
- The M3 labelling method (sub-gap codes per mistake), as a way to read failures beyond δ_norm.
