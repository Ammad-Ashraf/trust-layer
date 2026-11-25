# R3 · Container test of the 0017 Prospino check — PASSED
- Ran `build_agent_folder.py` (repo `70b664c`, clean) and `bash scripts/gate_container_test.sh` (part A only, no Claude call, $0) on 2026-11-26 01:45 local; image `lhc-bench@sha256:8820ecd3…`, Python 3.11.15. Output: `container-test.txt`.
- ok 1, 2, 3, 4, 5 and 7 all pass. The new ok 7: a σ labelled `prospino` is sent back (exit 2) when there is no Prospino output, and passes (exit 0) when the run's own `prospino.dat` matches; then `CONTAINER TEST PASSED`.
- Nothing odd. The script has no ok 6 without `--claude-hook`, which was not needed here.
