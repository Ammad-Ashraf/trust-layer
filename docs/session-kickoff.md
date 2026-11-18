# Starting a new session

You don't need to paste the project's context into a new session. The repo carries it.

## What a new session reads, and when

| What | How it's loaded | Holds |
| --- | --- | --- |
| `CLAUDE.md` | automatically, every session | the project, the rules, the map of where things live |
| Claude's memory | automatically, every session | how Ammad likes work reported (short bullets, plain words, analogies) |
| `/session-start` | when you type it | the last lab-log lines, the current milestone, decisions due soon |
| `/session-end` | when you type it | writes the lab-log line, updates the roadmap and decisions |

Each session starts small. It reads only what the current task needs, so its context window stays free for the work itself.

## Kickoff prompt (copy, then fill in the last line)

```
/session-start
Today's goal: <one line, e.g. "M2 — fill the sus-16-034 ledger with me">
```

That's all a session needs. End every session with `/session-end`, so the next one can pick up from the lab log.

## Rules that keep sessions in sync

- **One machine edits code.** The Windows laptop edits; the runner only adds files under `experiments/*/runs/`.
- **Pull before you start, push before you stop.** On either machine, `git pull` first and push at the end.
- **The lab log is the hand-off.** If it isn't in `lab-log.md`, `docs/roadmap.md` or `docs/decisions/`, the next session won't know it.
