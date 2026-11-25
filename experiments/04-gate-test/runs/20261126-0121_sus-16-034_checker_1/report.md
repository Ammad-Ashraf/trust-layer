# R2 · Checker-arm run — FAILED before launch (Collider-Bench rejects the agent name)

- **Ran:** R2 steps 1–3 on 2026-11-26 01:21 local. `build_agent_folder.py` (repo `da69956`, clean) and `cp -r build/agent/simple_ledger external/collider-bench/agents/`. MCP isolation was applied as in the smoke run: Mattermost was removed from user scope and `ENABLE_CLAUDEAI_MCP_SERVERS=false` was set. Then `scripts/run-agent --config ../../experiments/04-gate-test/harness-config.yaml` from `external/collider-bench` (submodule `2986d8b`).
- **Failure:** config validation stops the run before any workspace or model call. The output is in `run-agent.log`:
  `ValueError: ../../experiments/04-gate-test/harness-config.yaml: agent='simple_ledger'; must be one of ['simple']`.
  It comes from `agent_runtime/config.py:43`, `_ALLOWED_AGENTS = {"simple"}`, which is checked at line 100. Copying a folder into `agents/` is not enough; the name is hard-coded in the allow-list.
- **Cost:** $0. No run dir was created, Claude was never called, and there is no score or postrun check.
- **Also odd:** the first launch attempt failed even earlier with `activate_lhc_analysis: no harness-ready Python`. `run-agent` needs `external/collider-bench/.venv` activated first (`source .venv/bin/activate`), which runner-tasks.md doesn't say. The second attempt used it and reached the error above.
- **Not fixed here** (runner rule 6, and the submodule is never edited). Two ways out, for the Windows side: keep `agent: simple` and attach the gate some other way, or patch the allow-list in a derived config/fork (that's a decision).
- **Cleaned up:** `external/collider-bench/agents/simple_ledger` removed, so the submodule is clean. Mattermost was re-added, and `~/.claude/settings.json` was restored; both are checked identical to the backups taken just before.
