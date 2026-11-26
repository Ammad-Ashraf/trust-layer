# Starting Study B on Israr's laptop (for Ammad)

From here on, Study B runs entirely on Israr's laptop, in a Claude session on **Israr's Max account**. You do two things by hand, once. Claude does the rest: test run, pilot, all 36 runs, labelling, results table.

## 1. Make the login key (once, about 2 minutes)

The benchmark runs need their own long-lasting key to Israr's Max account, so they never clash with the Claude session you're talking to. Do this with Israr's OK, because it logs in to his account.

On Israr's laptop, open a terminal and type:

```bash
mkdir -p ~/.config/trust-layer && chmod 700 ~/.config/trust-layer
claude setup-token
```

- A browser opens. Sign in with **Israr's Max account** and click **Authorize**.
- The terminal prints a long key. Copy it.

```bash
nano ~/.config/trust-layer/claude-oauth-token
```

- Paste the key, then press **Ctrl+O**, **Enter**, **Ctrl+X**.

```bash
chmod 600 ~/.config/trust-layer/claude-oauth-token
```

Don't paste the key anywhere else: not in chat, not in a file in the repo.

## 2. Open Claude in the repo folder

In a terminal on Israr's laptop (logged in to Claude with **Israr's account**):

```bash
cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer
claude
```

## 3. Type this one line

```
Run `git checkout main && git pull --ff-only`, then read the "Kickoff prompt" section of docs/study-b-start.md and follow it exactly.
```

That's all. The agent pulls the latest changes, finds the prompt below, and starts. (You can also paste the whole prompt below directly instead.)

## Kickoff prompt

> **For the agent on Israr's laptop.** You are the runner session for the trust-layer project. Your job is to run Study B to the end.
>
> 1. Make sure the repo is current: `git checkout main && git pull --ff-only && git fetch --tags && git submodule sync && git submodule update --init`. If the pull fails, stop and tell me why.
> 2. Read, in this order: `CLAUDE.md` (the rules, especially "Two machines" and "Fairness"), then `docs/runner-tasks.md` (your work queue: the "How to work this queue" rules and the Study B section, R5–R8).
> 3. Find the first Study B task that isn't done: check what is committed under `experiments/04-gate-test/runs/*study-b-smoke*`, `experiments/03-study-b/runs/`, and whether the tag `study-b-v1` exists. Run `python3 scripts/study_b.py status` once R5 has passed. Tell me in 2–3 lines where we are and what you'll do next. Then start it.
> 4. Work through R5 → R6 → R7 → R8 in order, following each task's go/no-go rule exactly. Don't skip a rule, and don't continue past a "stop".
> 5. Hard rules:
>    - Never print, `cat`, copy or commit the login key in `~/.config/trust-layer/`. Only check that it exists (`test -s`). If it's missing, ask me to do step 1 of `docs/study-b-start.md`, and wait.
>    - Never edit code or docs. Commit only what the tasks allow: run folders, `labels.yaml`, generated results, the one tag, and lab-log lines.
>    - Launch long runs only through the `systemd-run …` commands in the tasks, and never start a second copy while one is active.
>    - If something fails, write a `report.md` where the task says, commit and push it, then tell me in plain words what happened and stop.
> 6. While runs are going (they take hours), do R8 labelling. When you stop for the day or I come back, tell me in 2–5 short bullets: what finished, what's running, what's next.

## Coming back later (a new session)

Same steps 2 and 3. The kickoff prompt makes the agent work out where it left off from what is committed, so nothing needs to be remembered between sessions. To just check progress, ask: *"What's the Study B status?"*.

## What happens next

| Step | What Claude does | Time |
| --- | --- | --- |
| R5 | One test run (Haiku 4.5, about 10 min). If it passes, tags the code `study-b-v1` | under 1 h |
| R6 | The pilot: 3 runs. If the pilot meets the fixed rules, it carries straight on | 2–8 h |
| R7 | The other 33 runs, one at a time, in the background | 1–3 weeks |
| R8 | Reads every transcript, labels the mistakes, builds the results table | while R7 runs, and after |

**While it runs:**
- Keep the laptop **plugged in, lid open**.
- Israr can still use his laptop and his Claude normally. His own use counts against the same Max limits, and the script waits automatically when usage is high.

**To check progress:** open Claude in the repo folder and ask *"What's the Study B status?"*. It runs `python3 scripts/study_b.py status`. Everything is also on GitHub: one folder per run under `experiments/03-study-b/runs/`.

**If Claude stops and reports a problem:** it writes a `report.md` saying what went wrong. Bring that to the Windows session (this project's builder Claude) to fix it; the runner doesn't change code.

**When it's done:** the results are in `experiments/03-study-b/results/study-b.md`, and Claude writes `experiments/03-study-b/runs/STUDY-B-DONE.md` with a short summary.
