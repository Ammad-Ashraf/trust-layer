# Smoke run review (2026-11-18)

Review by Claude (Windows laptop) of branch `runs/smoke-run-20261118` (commit `8e90328`, pushed by the runner). The branch is fetched but **not merged**. The runner's own write-up is in `runs/20261118-0109_sus-16-046_baseline_1/` (`notes.md`, `attachment-points-observed.md`). This file adds checks against the Collider-Bench code and paper, and lists the decisions for Ammad.

## 1. What the branch contains

- 11 files, all under `experiments/00-smoke-run/runs/20261118-0109_sus-16-046_baseline_1/`, so the runner rule held. A scan for tokens, keys and passwords found nothing.
- It contains: `manifest.yaml` (fully pinned: CB commit `2986d8b`, image digest, model, hardware, N_gen), the harness config, `score.json`, `run_info.json`, the submitted YAML, the agent's report, 2 plots, a draft `labels.yaml`, `notes.md` and the attachment-point map.
- **Not committed:**
  - the transcript (`workspace/session.jsonl`, 1.2 MB);
  - the agent's `analysis.py`.
  
  Both stay on the runner. The full transcript read (M3) and the root-cause check below need them.

## 2. Result

| | |
| --- | --- |
| Task | `sus-16-046_sim-T5Wg`, Sonnet 4.6, effort max, OAuth, no checker |
| Outcome | exit 0, 4/4 bins, **fail**: δ_norm 0.98, norm rel. L² 0.995, shape rel. L² 0.92 |
| Cost / time | $5.68 API-equivalent, 27.8 min, 107 turns, 1.4 GB disk |

- **Consistent with the paper.** The Collider-Bench paper reports Sonnet 4.6 on this task at 0.61 ± 0.46 (Table 2, Appendix D), so one run at 0.98 is inside that spread.
- **M1's done-when is met.** The roadmap says "one task runs end to end on the runner; lab log started". The run scored and the manifest is fully pinned.

## 3. Why it failed: ε, not σ, L or units

- **The agent got σ, L and units right:**
  - σ = 3.96 fb (Prospino NLO, pb→fb converted correctly);
  - L = 35.9 fb⁻¹;
  - the right mass point.
- **The efficiency was far too low.** Only 93 of 10,000 events pass, ε = 0.93%. The reference implies about 38.6% (54.8 expected events ÷ 142 produced), so the yield is about 50× too low.
- **The shape is also wrong.** The agent's S_T falls with energy, where CMS's rises.
- **My hypothesis (unverified): photon–jet overlap.**
  - In Delphes, the photon is also clustered into a jet.
  - The agent applied ΔR(γ, jet) > 0.5 against *all* jets, with no pT floor and no removal of the jet that is the photon (its report, deviation 5).
  - That would veto most events that have the hard signal photon (about 850 GeV from χ̃⁰₁ → γG̃). The survivors would be odd, low-S_T events.
  - This fits both symptoms: the 20% preselection pass rate and the inverted shape.
  - **To check:** read `analysis.py` on the runner.
- **Labels.**
  - If the hypothesis holds, the primary label is **3b (conventions: overlap removal)**, with **3c (no sanity check on a 0.93% acceptance)** as secondary.
  - The runner's draft has only 3c.
  - There is no Gap-1 error in this run.

## 4. What this means for Phase 1

- **C1–C5 would pass this run.** Every factor in the ledger is right except ε, which the pipeline computes.
- **Collider-Bench's metric mixes things up.** Its "normalization" metric (δ_norm) lumps kinematic ε failures together with σ × L × BR errors. "Fails δ_norm" does not mean "has a 1a–1e error".
- **The paper still backs the Phase 1 target:**
  - Section 4.3 says normalization is "a recurring bottleneck".
  - It names the failures C2, C4 and C5 target: wrong process or mass point, mixed conventions, a computed rate not propagated.
  - Section 4.4 suggests a "specialized normalization or cross-section-checking module".
  - It gives no counts, though.
- **The risk the plan already names is now concrete.** If most baseline failures are ε or kinematics, Study B has little for the checker to catch. One run is a hint, not evidence.
- **Study A is unaffected.** It injects 1a–1e errors directly.

## 5. Attachment points, checked against Collider-Bench code

I confirmed the runner's observations in the source and found one better attachment route for the ledger CLI.

**1. Ledger CLI → agent.**
- Collider-Bench's own plug-in point is an agent folder.
  - Each script in `agents/<name>/runtime/bin/` is symlinked into `workspace/bin/` (`agent_runtime/workspace.py`, `build_workspace`).
  - `agents/<name>/runtime/` is mounted read-only (`agent_runtime/launch.py:321-323`).
  - Workspace templates come from `agents/<name>/runtime/templates/workspace/`.
- So a `simple-ledger` agent, a copy of `simple` plus `bin/record-quantity` plus one paragraph in its AGENTS.md, gives the agent `bin/record-quantity`. No image change and no PATH change are needed.
- The baseline arm keeps using upstream `simple`, unchanged.
- The catch is that this folder lives inside the submodule. See decision D2.
- `pint` is missing from the image's `lhc_analysis` env, while `pyyaml` is present. See decision D3.

**2. Gate.**
- A Stop hook fires inside the container, and the exit-2 message reaches the agent as a user turn. The runner tested this with Haiku for $0.03.
- The hook config comes from the host user's `~/.claude/settings.json`. It is copied into the run's fake home together with `.claude.json` and the credentials (`agent_runtime/vendors.py:224-227`).
- Not covered yet:
  - **Tampering:** the agent runs with `--dangerously-skip-permissions` and can write to its fake home, so it could edit out the hook. The bounce log should therefore be written outside the workspace, and the settings checked for changes after each run.
  - **Message paths:** gate messages must give absolute paths.

**3. Artifacts.**
- The transcript is `workspace/session.jsonl` (`launch.py:162`). Collider-Bench's CLAUDE.md is out of date on this.
- `.claude_home/` holds a copy of the OAuth credentials. It must never leave the runner.

**4. `bin/run-analysis`.** It works as documented. The agent used it 7 times and never ran `python analysis.py` directly.

**Extra tools.** The harness blocks only `ScheduleWakeup` (`vendors.py:217`). The newer CLI adds tools that touch the account (RemoteTrigger, CronCreate, PushNotification, SendMessage, Workflow). We could block them with deny rules in the subject user's settings. Whether deny rules still apply under `--dangerously-skip-permissions` is not tested yet.

## 6. Decisions for Ammad (options → lean)

D1 was taken: Ammad merged the branch on 2026-11-18. D2–D7 are recorded as open decisions [0008](../../../docs/decisions/0008-ledger-agent-folder.md)–[0013](../../../docs/decisions/0013-baseline-failure-mix.md).

- **D1. Merge the branch?** Lean: yes, merge as is. Then carry the durable points into:
  - `integration/attachment-points.md`;
  - `experiments/00-smoke-run/README.md`;
  - the roadmap (M1 ✅);
  - the lab log.
- **D2. Where does the `simple-ledger` agent folder live?**
  - (a) Fork Collider-Bench, add one folder, and pin the submodule to the fork commit. Lean: it is additive, pinned and reviewable, and upstream code is untouched.
  - (b) A setup script symlinks `integration/agent/` into the submodule at run time. No fork is needed, but the submodule is dirty and the run is not pinned.
  - (c) A derived image. This changes the image digest and is the heaviest option.
- **D3. `pint` inside the container.**
  - (a) Drop `pint` for the in-container ledger and use a fixed pb/fb/fb⁻¹ table, standard library only. Lean: fewer moving parts.
  - (b) Vendor `pint` into the read-only mount.
- **D4. Subject isolation.** Lean: a dedicated runner OS user (e.g. `tlsubject`) whose home holds only the subject's settings, the hook and a login or API key. This fixes the MCP/connector leak, keeps the builder's settings out, and leaves the submodule untouched.
- **D5. Auth for measured runs.** Lean: an API key with a spend limit for Study B. OAuth's refresh-token race and its 5-hour limits make long, parallel runs fragile. OAuth is fine for one-off runs.
- **D6. Commit transcripts?** Decision 0004 deferred this until the size was known. It is 1.2 MB, so lean: commit `session.jsonl.gz`, `analysis.py` and `report.md` per run. Never commit `sims/`, `data/` or `.claude_home/`.
- **D7. Study B power check.** Lean: before committing Study B tasks, run about 3 cheap baseline runs (Sonnet, 3 tasks) and label them. Count how many failures are 1a–1e versus ε or kinematics. Add an ε-plausibility check (3c) to the parking lot, not to Phase 1.

## 7. Small fixes on the Windows laptop (after D1)

- Add `ColliderBench/tasks/shared/*/reference` to the FORBIDDEN list in `tests/test_fairness.py`.
- Put the full task id (`sus-16-046_sim-T5Wg`) in `manifest.yaml`.
- Rename `tasks/` folders to match the full task ids.
- Add three notes to `experiments/00-smoke-run/README.md`:
  - the image is 8.5 GB unpacked;
  - each run takes 1.4 GB of disk;
  - the runner's Python is 3.14, outside Collider-Bench's CI matrix, but the tests pass.
