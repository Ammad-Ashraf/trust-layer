# 04-gate-test

- **Status:** R1 passed; R2 to rerun (runner tasks R1 and R2 in [`docs/runner-tasks.md`](../../docs/runner-tasks.md))
- **Question:** Does the built `simple_ledger` agent folder work inside the real Collider-Bench container? Concretely: the ledger CLI, the gate, the bounce log, and whether Claude Code fires a Stop hook registered in the workspace's project settings.
- **Setup:**
  - R1 is a container test with no API cost (`scripts/gate_container_test.sh`), plus a few-cent check with Haiku.
  - R2 is one real harness run: `agent: simple_ledger`, task `sus-16-034_sim-TChiWZ`, Haiku 4.5, OAuth (see `harness-config.yaml`).
- **Output:** M4's "done when": the gate blocks a bad ledger in a real test run.
- **Not a measured experiment:** this is plumbing. Its numbers don't go into Study B.

## Findings

- **R1 passed (26 Nov, `da69956`).** Inside the image (Python 3.11.15), with no `pint`:
  - the gate sent an empty workspace back with an actionable message;
  - the ledger CLI recorded all factors and detected the task from the run folder;
  - matching results passed, and a bin 10× off was sent back;
  - the bounce log recorded every decision.
  - **Ok 6:** with the host's Claude Code and Haiku, a Stop hook in the workspace's `.claude/settings.json` fired (1 gate call, a C3 bounce on the empty ledger). The gate reaches the agent the way the design assumed.
- **R2 attempt 1 (`59477a5`)** stopped before launch at $0, because Collider-Bench's launcher only accepts the agent name `simple`. It is fixed by `scripts/run-checker-arm`, with no submodule edit (findings log F5).
