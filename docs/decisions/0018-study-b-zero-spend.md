# 0018 — Study B spends nothing: Israr's Max subscription, on the runner laptop

- **Status:** decided
- **Date:** 2026-11-27
- **Supersedes:** 0006 (budget cap); the Study B parts of 0002 (rent 128 vCPU) and 0011 (API key for Study B)

## Question

Can Study B (36 runs: 18 Sonnet 4.6 per 0005, 18 Haiku 4.5 per 0007) run with no money spent?

## Decision (Ammad)

Yes. No API key, no rented machine, no other spend. Study B runs on Israr's laptop ([`runner-machine.md`](../runner-machine.md)) and logs in with Israr's Claude Max subscription. Why: Ammad won't spend money on Phase 1, and Max gives enough usage for one run at a time.

## What this changes, and how we handle it

1. **Login clash (fix designed by Claude).** The harness copies `~/.claude/.credentials.json` into each run's fake home and copies it back after the run (`_sync_credentials_back_to_host` in `agent_runtime/sandbox.py`). The login token rotates: whoever renews it first makes the other copy stale. The runner's own Claude session runs as user `israr` with the same login. If it renews during a 2.5 h run, the agent in the container gets a 401 partway through.
   - **Fix:** run every measured run as the dedicated `tlsubject` user (0010, already decided), with **its own** `claude` login to Israr's account. A separate login has its own token chain, so the runner session can't make it stale. Israr does that login himself.
   - **Rules:** one run at a time; nothing else ever logs in as `tlsubject`; launch runs detached (`systemd-run --user` or `nohup`) so they don't depend on a Claude session staying open. The harness's copy-back then keeps the chain current from one run to the next.
   - **Fallback if `tlsubject` is refused:** run as `israr`, launch detached, and keep the runner session closed until the run ends.
   - **Optional hardening, in the Collider-Bench fork (0008):** a long-lived token from `claude setup-token`, passed as `CLAUDE_CODE_OAUTH_TOKEN` by adding it to `CLAUDE_SPEC.secret_env_names`. It doesn't rotate, so the clash can't happen. Only if the test below fails.
   - **Test:** runner task R5 (`docs/runner-tasks.md`).
2. **Usage limits.** Max still has 5-hour and weekly limits, shared with Israr's own use. Rule fixed before Study B: a run that ends on a usage-limit or auth error is **void**. It is logged, never scored, and rerun in the same arm. The void count per arm is reported.
3. **32 threads instead of 128 cores.** The paper gave each agent 128 cores for 2.5 h; this laptop has 32 threads. Both arms get the same machine and limit, so the with/without comparison stays fair, but more runs may end by timeout (the confound 0002 named). Handling: record N_gen, wall-clock and "ended by timeout" per run, and report the timeout rate per arm. If the M6 baseline runs time out often, raise the walltime equally for both arms in the fork (a later decision).
4. **Throughput.** 36 runs one at a time, at 0.5–2.5 h each, is 18–90 machine-hours. That fits 16 Dec–5 Jan.
