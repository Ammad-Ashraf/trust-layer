# Container integration

How the ledger CLI and the gate get into the Collider-Bench container, without changing the benchmark image or upstream code. Background: [`../attachment-points.md`](../attachment-points.md), decisions 0008 (fork + one agent folder) and 0009 (no `pint` in the container).

## What gets mounted

Collider-Bench mounts `agents/<name>/runtime/` read-only at the same absolute path inside the container, and symlinks every `runtime/bin/*` script into the agent's `workspace/bin/`. So everything we ship lives in one agent folder, **`agents/simple_ledger/`**, built by:

```
python3 scripts/build_agent_folder.py                       # -> build/agent/simple_ledger (git-ignored)
python3 scripts/build_agent_folder.py --out <fork>/agents/simple_ledger --into-fork
```

The name is `simple_ledger`, not `simple-ledger`: Collider-Bench imports `agents.<name>.run` as a Python module, so the name can't contain hyphens.

| Path in the folder | What | The agent sees it as |
| --- | --- | --- |
| `run.py` | launcher: same prompt as `simple`; writes `workspace/.claude/settings.json` with the Stop hook | — |
| `AGENTS.md` | upstream text + the ledger paragraph (`../agent/AGENTS-ledger.md`) | `agent_context/AGENTS.md` |
| `runtime/bin/record-quantity` | ledger CLI shim | `bin/record-quantity` |
| `runtime/hooks/trustlayer-gate` | Stop-hook shim | not on `bin/` |
| `runtime/lib/trustlayer/` | the checker source (`*.py` only) | readable, not on any path |
| `runtime/task-context/*.yaml` | public task facts (`../task-context/`) | readable |
| `runtime/config.yaml` | τ = 0.05 (decision 0016), max 3 bounces | — |
| `runtime/BUILD-INFO.yaml` | trust-layer commit, dirty flag, build time | — |

The shims run `/opt/conda/envs/lhc_analysis/bin/python -s -P` with `PYTHONPATH=runtime/lib`. `-P` stops a planted `trustlayer.py` in the workspace from shadowing ours.

## How the gate is switched on (checker arm only)

The harness copies the *host user's* `~/.claude/settings.json` into every run, so a hook placed there would fire in baseline runs too. Instead, `simple_ledger/run.py` wraps Collider-Bench's `build_workspace` and writes a **project-level** `workspace/.claude/settings.json` holding only the Stop hook. Baseline runs use upstream `simple` and never get it. Upstream code is not edited; our `run.py` replaces the function at run time.

Confirmed 2026-11-26 (runner task R1, ok 6): Claude Code in `-p --dangerously-skip-permissions` mode fires a Stop hook from the workspace's project settings.

**Launching:** Collider-Bench's `scripts/run-agent` only accepts the agent `simple`. The checker arm is launched with `scripts/run-checker-arm --config <harness config without agent:>`, which runs the same `run_with_compute` and `launch_single_run` with `PY_MODULE=agents.simple_ledger.run` (finding F5).

## Runner checklist (M4 steps 7–8)

1. `git pull`, then `python3 scripts/build_agent_folder.py`.
2. `bash scripts/gate_container_test.sh` (free) and, once, `--claude-hook` (Haiku, a few cents).
3. The folder comes with the submodule: `git submodule update --init` checks out the fork commit that contains `agents/simple_ledger/`. Then run one task with `bash scripts/run-checker-arm --config <config>`.
4. After the run: `python3 scripts/postrun_check.py <harness run dir> experiments/<exp>/runs/<run-id>/`. It copies the bounce log and prints `bounces`, `gate_final_event`, `tampered` and `gate_error` for the manifest.
5. **The fork** (decision 0008, done 27 Nov): [`Ammad-Ashraf/Collider-Bench`](https://github.com/Ammad-Ashraf/Collider-Bench), branch `trust-layer` = upstream `2986d8b` plus `agents/simple_ledger/` and the 10 h walltime in the three Study B `task.toml` files (decision 0019). The submodule is pinned to that branch. **After any change to `src/` or `integration/`:** commit it, rebuild into a clone of the fork on the `trust-layer` branch (`--out <clone>/agents/simple_ledger --collider-bench <clone> --into-fork`), set the exec bit on the shims and `run-analysis` (`git add --chmod=+x`, needed on Windows), commit, push, and repin the submodule here. `runtime/BUILD-INFO.yaml` must name a clean trust-layer commit.
