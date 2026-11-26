# Runner tasks (Israr's machine)

The work queue for the runner: the Linux laptop that runs Collider-Bench. Ammad pulls the repo there and tells the runner's Claude session: **"Read `docs/runner-tasks.md` and do the open tasks."** Everything a task needs is written here; no instructions come in chat.

## How to work this queue (runner session, read first)

1. `cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer`, then `git checkout main && git pull --ff-only`. Stop and report if the pull fails.
2. Do the tasks marked **open**, in order. Skip **done** ones. Don't start a task whose "Needs" isn't met.
3. **Commit only under `experiments/*/runs/`** (CLAUDE.md, two-machine rule). Never commit code, docs, `.claude_home/`, `workspace/sims`, `workspace/data` or credentials. Never commit changes inside `external/collider-bench/`.
4. Each task ends with a `report.md` in its run folder (what ran, the numbers, anything odd, 5–10 lines), committed and pushed. The Windows session reads that report and marks the task done here. The runner never edits this file.
5. Before committing any transcript or log, scan it for secrets: `sk-ant`, `Bearer`, `oauth`, `refresh_token`, `access_token`, `api_key`, `password`. On a real secret, stop and report; don't commit.
6. If a step fails, write what failed into `report.md`, commit that, and stop. Don't improvise fixes to our code on this machine.

Machine specs: [`runner-machine.md`](runner-machine.md).

Paths used below: `CB=external/collider-bench`. A harness run folder is `$CB/runs/<runner>_<model>/<task>_<agent-id>/` (written `<RUN>`).

---

### R5 · `tlsubject` user and the login-clash test (decisions 0010, 0018): **open**

**Needs:** Israr's OK, and Part A done by Israr by hand (it needs `sudo` and his Claude login). The runner session never runs `sudo` beyond the one rule Part A adds, and never sees or copies a credential value.

**Why:** Study B runs on Israr's Max subscription. The runner session (user `israr`) and the run in the container share one rotating login, so a renewal by the runner session mid-run breaks the run. Running as `tlsubject`, with its own login, gives the run its own token chain. It also gives the subject a clean home with no MCP servers or connectors.

**Part A (by hand, at the laptop, about 20 min plus the image download):** the step-by-step is in [`runner-r5-setup.md`](runner-r5-setup.md). In short: create `tlsubject`, enable linger, add the one sudoers rule (`israr ALL=(tlsubject) NOPASSWD: ALL`), give `tlsubject` read access to `israr`'s checkout, clone it, install Claude Code 2.1.326, pull the image, and log in with Israr's Max account.

**Part B (runner session):** first, in `israr`'s checkout, switch the submodule to the fork. R2's hand-copied `agents/simple_ledger` is in the way, so delete it first: `rm -rf $CB/agents/simple_ledger && git submodule sync && git submodule update --init`, then check `git -C $CB log --oneline -1` shows `d8ac871`. Then as `tlsubject`, always via `sudo -iu tlsubject env XDG_RUNTIME_DIR=/run/user/$(id -u tlsubject) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u tlsubject)/bus bash -lc '…'`. Podman and `systemd-run --user` need those two variables; the sudoers rule allows only this, never root. Folder: `experiments/04-gate-test/runs/<YYYYMMDD-HHMM>_login-test/`.
1. Check the clean home: `~tlsubject/.claude.json` has no `mcpServers` entries, and `~tlsubject/.claude/settings.json` is missing or `{}`. Record yes/no; don't commit either file.
2. Record the login's `expiresAt` only (never the token): `jq .claudeAiOauth.expiresAt ~/.claude/.credentials.json`, for both `tlsubject` and `israr`.
3. As `tlsubject`, in `~/trust-layer`, after `git pull --ff-only && git submodule sync && git submodule update --init` (expect `d8ac871`) and the venv setup from R2: launch R2's config **detached**: `systemd-run --user --unit tl-login-test bash scripts/run-checker-arm --config experiments/04-gate-test/harness-config.yaml` (Haiku 4.5, about $1 API-equivalent, $0 on the subscription).
4. While it runs, keep this runner session working normally (that is the clash case). Watch with `journalctl --user -u tl-login-test`.
5. After it ends: did it finish without a 401 or auth error? Record `expiresAt` again for both users. Note whether `tlsubject`'s `expiresAt` was passed during the run, i.e. whether the renewal path was exercised. Check that the run's init event shows `mcp_servers: []`.
6. Start a second, short run the same way and stop it after its first turn (`systemd-run --user --unit tl-login-test-2 …`, then `systemctl --user stop tl-login-test-2`). It shows the copied-back login still works.
7. Copy the run's `report.md` inputs (`run_info.json`, `eval/score.json`, `launch.log`, the init event line) from `tlsubject`'s run folder into the folder above, scan them for secrets (queue rule 5), write `report.md`, commit and push.

**Pass:** both runs authenticate, the first finishes, and `israr`'s login still works afterwards.

---

## Done

- **R4 · Prospino LO for Study A: done** (`c765e58`, folder `experiments/02-study-a/runs/20261127-0032_prospino-lo`), $0. Stop 800: LO 15.9 / NLO 27.2 fb; wino 550: LO 23.09 / NLO 27.55 fb. Both NLO values within 9% of the published NLO+NLL.
- **R3 · Container test of the 0017 Prospino check: passed** (`3976e9b`, folder `20261126-0145_container-test-0017`), ok 1–5 and 7, $0.
- **R2 · One real checker-arm run (M4 step 8): ran** on attempt 2 (`aa8db45`, folder `20261126-0125_sus-16-034_checker_1`). Haiku 4.5, $1.13, 0 bounces, gate passed, not tampered. Attempt 1 (`59477a5`) never launched (agent-name allow-list; fixed by `scripts/run-checker-arm`). Review: `experiments/04-gate-test/results/r2-review.md`.
- **R1 · Container test of the gate (M4 step 7): passed** on attempt 2 (`da69956`, folder `20261126-0119_container-test`), ok 1–6. Ok 6 confirms that Claude Code in `-p` mode fires a Stop hook from the workspace's `.claude/settings.json`. Attempt 1 (`2144354`) failed on a bug in the test script, fixed in `f713503`.
