# 00-smoke-run

- **Status:** done (2026-11-18). It was a plumbing test, not a measured run.
- **Question:** Does the Collider-Bench harness run end to end on the runner laptop?
- **Setup:**
  - Task `sus-16-046_sim-T5Wg`, Collider-Bench's own smoke task, chosen by Ammad instead of sus-16-034.
  - Sonnet 4.6 at effort max, OAuth on Ammad's subscription, no checker.
  - Config: Collider-Bench `configs/claude.yaml`, with only the model and auth changed.
- **Pinned** (in the run's `manifest.yaml`):
  - Collider-Bench commit `2986d8b`;
  - image digest `sha256:8820ecd3…`;
  - Claude Code 2.1.326;
  - runner laptop with 32 threads;
  - N_gen 10,000.
- **Rerun:** `scripts/run-agent --config <run>/harness-config.yaml`, run from `external/collider-bench` on the runner.

## Findings

- **Plumbing works.**
  - Exit 0, 4/4 bins filled and scored.
  - 27.8 min, 107 turns, $5.68 API-equivalent.
  - 1.4 GB of disk per run.
- **Score.**
  - δ_norm 0.98 and shape rel. L² 0.92, so it fails.
  - The paper reports Sonnet 4.6 on this task at 0.61 ± 0.46, so one run at 0.98 is inside that spread.
- **The failure was ε, not σ, L or units.**
  - The agent got σ (3.96 fb from Prospino), L (35.9 fb⁻¹) and the mass point right.
  - The signal-region efficiency was 0.93%, against about 38.6% in the reference.
  - Checks C1–C5 would have passed this run. That is expected: it was a selection mistake, which is out of Phase 1 scope. The paper shows such runs are the exception (decision [0014](../../docs/decisions/0014-drop-failure-mix-runs.md)).
  - **Cause, confirmed in the M3 read (26 Nov):** the stock Delphes CMS card doesn't treat the gravitino as invisible, so it turns into a jet and the missing momentum is lost. Truth MET is above 300 GeV in 72% of events; reco MET only in 9%. The 18 Nov photon–jet guess is ruled out. Labels are 3a, 3b, 3c, 3d plus one uncoded slip, and no Gap-1 errors → [`results/m3-review.md`](results/m3-review.md).
- **All four attachment points are mapped** → [`integration/attachment-points.md`](../../integration/attachment-points.md). A Stop hook fires inside the container and its rejection reaches the agent.
- **Setup problems hit:**
  - The runner had no Podman and no `python3-venv`.
  - The image is 3.9 GB to download and 8.5 GB unpacked; the docs say about 3.5 GB.
  - The image does not include `claude`; the harness mounts the host binary.
  - The host's MCP servers and connectors leaked into the subject agent (decision [0010](../../docs/decisions/0010-subject-isolation.md)).
  - There is a risk that the host and the container both refresh the same OAuth token during a long run (decision [0011](../../docs/decisions/0011-auth-for-measured-runs.md)).
  - The runner's Python is 3.14, outside Collider-Bench's CI matrix, but all tests pass.

Full details are in [`results/smoke-run-review.md`](results/smoke-run-review.md) and the run folder's `notes.md`.
