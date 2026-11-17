# Attachment points — observed in the smoke run (2026-11-18)

Written on the runner, which only commits under `runs/`. Carry into `integration/attachment-points.md` on the Windows laptop.
`<RUN>` = `external/collider-bench/runs/claude_sonnet-4-6/sus-16-046_sim-T5Wg_GayDrell_50621269` (absolute path on the runner: `/home/israr/Documents/Ammad-Particle-Physics/trust-layer/<RUN>`).

## 1. Where the ledger lives

- **Agent workspace:** `<RUN>/workspace/`, bind-mounted read-write at the *same absolute path* inside the container; it is the container's working directory and the agent's `cwd`. It holds `agent_context/{TASK,AGENTS,TOOLS}.md`, `prompt.txt`, `papers/<paper>.pdf`, `results/<template>.yaml`, `object_efficiencies/`, `bin/`, and a `tools -> ColliderBench/tools` symlink. The agent writes `analysis.py`, `datasets.yaml`, `report.md`, `sims/`, `data/` there.
- **PATH:** fixed in `agent_runtime/sandbox.py` (`container_path`): `/opt/sim/MG5_aMC_v3_7_0/bin`, `/opt/sim/delphes`, `/opt/node-global/bin`, `/opt/conda/envs/lhc_analysis/bin`, then system dirs. `workspace/bin` is **not** on PATH: the agent calls tools as `bin/<tool>`, and `workspace/bin/*` are symlinks into the host repo (`ColliderBench/bin/*`, `agents/simple/runtime/bin/run-analysis`), mounted read-only.
- **How `record-quantity` can reach the agent without editing the submodule:** not solved yet. Every PATH dir is either baked into the image or hard-coded in `sandbox.py`. Candidates to design on the Windows laptop: (a) call it by absolute path from a mounted location; (b) install it into the image's `lhc_analysis` env via a derived image (changes the pinned digest); (c) document it as `bin/record-quantity`-style, which needs the workspace builder. Each is a trade-off between "no benchmark changes" and "agent can find it".
- **Ledger file location for the gate:** anywhere under `<RUN>/workspace/` is visible to both the agent and a Stop hook (same absolute path inside and outside the container).

## 2. Where the gate fires

- **Hook config location:** the harness builds a fake `$HOME` at `<RUN>/.claude_home/` and copies **from the host user's real home**: `~/.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json` (`CLAUDE_SPEC.home_files` in `agent_runtime/vendors.py`). So a Stop hook placed in the host `~/.claude/settings.json` reaches the agent. **Problem:** that couples the builder's and the subject's settings on one host user, and it is also how Mattermost and the claude.ai connectors would have leaked in (we disabled them for this run). Needs a design: a dedicated runner OS user whose home holds only the subject settings is the cleanest option that leaves the submodule untouched.
- **Does a Stop hook fire there?** **Yes.** Tested separately (same image, same host binary, throwaway `$HOME`, `claude -p`, Haiku 4.5, $0.03): the hook fired on the first stop and again after the agent's fix.
- **Does the rejection reach the agent?** **Yes.** Exit code 2 + stderr arrived as a user turn: `Stop hook feedback: [<hook path>]: <message>`. The agent acted on it and the second stop was allowed. Design note: the agent wrote the requested file next to the *hook script* rather than its `cwd`, so gate messages must name absolute paths (e.g. the ledger's full path).
- Hook scripts must live on a path mounted into the container (the fake home or the workspace; the rest of the host repo is not mounted).

## 3. Where run artifacts land

- **Transcript:** `<RUN>/workspace/session.jsonl` (stream-json, 1.2 MB for 107 turns / 28 min). The Collider-Bench CLAUDE.md says `*.stream.jsonl` at the run root; in this version it is `workspace/session.jsonl`. A second copy of the conversation is in `<RUN>/.claude_home/.claude/projects/*/<session-id>.jsonl`.
- **Submitted results YAML:** `<RUN>/workspace/results/histogram_T5Wg.yaml` (filled in place).
- **Evaluator output:** `<RUN>/eval/score.json` + `<RUN>/eval/plots/*.png`; run metadata, cost and tokens in `<RUN>/run_info.json`.
- **Size per run:** 1.4 GB total, almost all simulation output (`workspace/sims` 816 MB, `workspace/data` 538 MB). Budget ~1.5 GB of disk per run at N_gen = 10k.
- **Secrets:** `<RUN>/.claude_home/` holds a copy of the OAuth credentials. Never copy it out of the (git-ignored) Collider-Bench `runs/` dir.

## 4. What `bin/run-analysis` activates

- **Environment:** conda env `lhc_analysis` at `/opt/conda/envs/lhc_analysis` (Python 3.11.15), already first on the image PATH; `run-analysis` sources `agent_runtime/shell/agent_env.sh`, finds the harness-ready Python, sets `PYTHONPATH=<repo root>`, runs `agent_runtime/preflight.py:check_analysis(datasets.yaml, analysis.py)`, then `timeout 14400 python analysis.py` under a `flock` (`.analysis.lock`). `ANALYSIS_NCPUS = nproc` (32 here).
- **Use in this run:** the agent called `bin/run-analysis` 7 times and never ran `python analysis.py` directly.
- **How our checks can run alongside it:** a Stop hook runs inside the container as the agent's user, so the hook can call `/opt/conda/envs/lhc_analysis/bin/python` with `trustlayer` importable from a read-only mount (add the mount via `PYTHONPATH` in the hook command). Checked in the image: `pyyaml` 6.0.3 is present, **`pint` is missing** from `lhc_analysis`. So either vendor `pint` into the read-only mount alongside `trustlayer`, or drop the `pint` dependency for the in-container part (the ledger only needs pb/fb/fb⁻¹).
