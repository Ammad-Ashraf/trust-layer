# 04-gate-test

- **Status:** not started (runner tasks R1 and R2 in [`docs/runner-tasks.md`](../../docs/runner-tasks.md))
- **Question:** Does the built `simple_ledger` agent folder work inside the real Collider-Bench container? Concretely: the ledger CLI, the gate, the bounce log, and whether Claude Code fires a Stop hook registered in the workspace's project settings.
- **Setup:**
  - R1 is a container test with no API cost (`scripts/gate_container_test.sh`), plus a few-cent check with Haiku.
  - R2 is one real harness run: `agent: simple_ledger`, task `sus-16-034_sim-TChiWZ`, Haiku 4.5, OAuth (see `harness-config.yaml`).
- **Output:** M4's "done when": the gate blocks a bad ledger in a real test run.
- **Not a measured experiment:** this is plumbing. Its numbers don't go into Study B.

## Findings

None yet.
