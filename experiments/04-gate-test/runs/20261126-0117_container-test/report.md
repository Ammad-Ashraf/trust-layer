# R1 · Container test of the gate — FAILED at ok 3 (test-script bug, not the gate)

- **Ran:** `python3 scripts/build_agent_folder.py` (repo at `d3bf640`, clean), then `bash scripts/gate_container_test.sh` on 2026-11-26 01:17 local. Image `ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3…`, `--pull=never --network=none`. Full output: `container-test.txt`. Build pins: `BUILD-INFO.yaml`.
- **Python in the image:** 3.11.15.
- **ok 1:** pass (empty workspace sent back, exit 2). **ok 2:** pass (ledger recorded, task detected, product 5.41).
- **ok 3:** FAIL. Expected exit 0 with matching results, but got exit 2: C5 says `results/histogram_TChiWZ.yaml: not valid YAML`.
- **ok 4, ok 5:** not reached. **ok 6 (`--claude-hook`):** not run. The `--claude-hook` mode reruns part A first, and under `set -e` it stops at the same failure. No Claude call was made, so this cost $0.
- **Cause (my diagnosis):** the Collider-Bench template writes each bin as flow YAML, `- {value: null}`. In `inside.sh`, `fill()` replaces `value: \S+`, and `\S+` swallows `null}` together with the closing brace. The file then has `- {value: 0.45` with no `}` (seen in the scratch copy). The gate was right to reject that file. The test's way of filling the template is the bug, e.g. `value: [^,}\s]+` would keep the brace.
- **Not fixed here** (runner rule 6: no code fixes on this machine). R2 was not started, because it needs R1 to pass, including ok 6.
- Scratch folder left in `/tmp/tl-gate-test.ocV1Ha/` (not committed).
