# R1 · Container test of the gate, attempt 2 — PASSED (ok 1–6)

- **Ran:** `python3 scripts/build_agent_folder.py` (repo at `f713503`, clean), then `bash scripts/gate_container_test.sh` (`container-test.txt`), then `--claude-hook` with `ENABLE_CLAUDEAI_MCP_SERVERS=false` (`claude-hook-test.txt`), on 2026-11-26 01:19 local. Image `ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3…`, `--pull=never --network=none`. Build pins: `BUILD-INFO.yaml`.
- **Python in the image:** 3.11.15. Host `claude` 2.1.326, host `python3` 3.14.4.
- **ok 1–5:** all pass, in both invocations: the empty workspace is sent back (exit 2), ledger product 5.41, matching results pass (exit 0), a 10x bin is sent back (exit 2), and the bounce log reads `bounce pass bounce`.
- **ok 6:** pass. Claude Code (Haiku 4.5, `-p`, `--dangerously-skip-permissions`) fired the workspace's project Stop hook: 1 gate call, `event: bounce` with C3 failing (`cross_section is missing`) on the empty ledger, and `stop_hook_active: false`.
- **Odd / worth knowing:** `claude.out` holds only `Error: Reached max turns (6)`. After the bounce, Haiku kept working, under the gate's feedback, until the `--max-turns 6` limit, so the gate was called only once. That is expected for this test, but a real run's turn cap will decide how many bounces an agent can get.
- Attempt 1 (`20261126-0117_container-test`, `2144354`) kept as is. Scratch folders are in `/tmp/tl-gate-test.BLrR50/` and `/tmp/tl-gate-test.qZTHm1/` (not committed).
