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

## 2. Start Claude and tell it to begin

```bash
cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer
git pull
claude
```

Then type:

> **Start Study B: read `docs/runner-tasks.md` and do the open tasks.**

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
